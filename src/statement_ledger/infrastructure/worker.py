"""Synchronous worker loop with a separate heartbeat connection and fenced result commit."""

from __future__ import annotations

import sqlite3
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

import httpx

from statement_ledger.contracts.runtime import JobRequest
from statement_ledger.core.errors import TransientFailure
from statement_ledger.core.validation import ReadLedger
from statement_ledger.infrastructure.artifacts import Artifact, LocalArtifactStore
from statement_ledger.infrastructure.logging import event
from statement_ledger.infrastructure.operations import OperationBlocked, OperationJournal
from statement_ledger.infrastructure.queue import LeaseLost, RuntimeQueue
from statement_ledger.infrastructure.settings import Settings
from statement_ledger.infrastructure.sqlite_store import Store


class StaleInput(RuntimeError):
    pass


class RetryableWork(TransientFailure):
    pass


def transient_error(error: BaseException) -> bool:
    if isinstance(error, (TransientFailure, httpx.TransportError, TimeoutError)):
        return True
    if isinstance(error, sqlite3.OperationalError):
        code = getattr(error, "sqlite_errorcode", 0)
        return (code & 255) in {sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED} or str(
            error
        ).lower() in {
            "database is locked",
            "database table is locked",
            "database schema is locked",
        }
    return False


@dataclass(frozen=True)
class RecordWrite:
    kind: str
    payload: dict[str, Any]
    expected_revision: int = 0


@dataclass
class PreparedResult:
    records: list[RecordWrite] = field(default_factory=list)
    artifacts: list[Artifact] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkContext:
    ledger: Any
    artifacts: LocalArtifactStore
    settings: Settings
    job_id: str
    attempt_id: str
    check_cancelled: Callable[[], None]
    operations: OperationJournal
    capture_response: Callable[..., str]


@dataclass(frozen=True)
class Handler:
    name: str
    version: int
    capability: str
    validate: Callable[[Any, JobRequest], None]
    prepare: Callable[[WorkContext, JobRequest], PreparedResult]
    writable_kinds: frozenset[str]


def input_check(ledger: Any, request: JobRequest) -> None:
    seen: set[tuple[str, str]] = set()
    for binding in request.inputs:
        key = (binding.kind, binding.id)
        if key in seen:
            raise ValueError("Duplicate input binding")
        seen.add(key)
        row = ledger.store.get(*key)
        if (
            row["revision"] != binding.revision
            or row["hash"] != binding.record_hash
            or not ledger.dependencies_current(*key)
        ):
            raise StaleInput("Job input changed, expired, or was invalidated")


class Worker:
    def __init__(
        self,
        ledger: Any,
        settings: Settings,
        handlers: dict[str, Handler],
        *,
        heartbeat: bool = True,
    ):
        self.ledger = ledger
        self.settings = settings
        self.handlers = handlers
        self.queue = RuntimeQueue(ledger.store)
        self.artifacts = LocalArtifactStore(
            settings.artifacts, max_bytes=settings.max_artifact_bytes
        )
        self.stop = threading.Event()
        self.heartbeat_enabled = heartbeat

    def _heartbeat(self, job: dict[str, Any], done: threading.Event, lost: threading.Event) -> None:
        # A heartbeat must never share the connection doing domain work.
        store = None
        try:
            store = Store(self.ledger.store.path, journal_mode=self.settings.journal_mode)
            queue = RuntimeQueue(store)
            while not done.wait(self.settings.heartbeat_seconds):
                try:
                    queue.heartbeat(
                        job["id"], job["lease_token"], lease_seconds=self.settings.lease_seconds
                    )
                except Exception:
                    lost.set()
                    return
        except Exception:
            lost.set()
        finally:
            if store is not None:
                store.close()

    def run_once(self) -> dict[str, Any] | None:
        self.queue.dispatch()
        job = self.queue.claim(
            self.settings.worker_capability, lease_seconds=self.settings.lease_seconds
        )
        if job is None:
            return None
        request = JobRequest.model_validate(job["payload"])
        done, lost = threading.Event(), threading.Event()
        thread = None
        start = time.monotonic()
        event(
            "work.started",
            run_id=request.run_id,
            job_id=job["id"],
            attempt_id=job["attempt_id"],
            handler=request.handler,
        )
        try:
            if self.heartbeat_enabled:
                thread = threading.Thread(
                    target=self._heartbeat, args=(job, done, lost), daemon=True
                )
                thread.start()
            handler = self.handlers.get(request.handler)
            if (
                handler is None
                or handler.version != request.handler_version
                or handler.capability != request.capability
            ):
                raise ValueError("Unknown or incompatible job handler")
            if request.config_sha256 != self.settings.execution_hash():
                raise StaleInput(
                    "Execution configuration changed; resubmit with a reviewed current configuration"
                )
            input_check(self.ledger, request)
            handler.validate(ReadLedger(self.ledger), request)

            def checkpoint() -> None:
                if lost.is_set():
                    raise LeaseLost("Worker lost its lease while processing")
                self.queue.assert_owned(job["id"], job["lease_token"])

            for value in request.artifacts.values():
                checkpoint()
                self.artifacts.verify(Artifact(**value.model_dump()))
            checkpoint()
            context = WorkContext(
                ReadLedger(self.ledger),
                self.artifacts,
                self.settings,
                job["id"],
                job["attempt_id"],
                checkpoint,
                OperationJournal(self.ledger.store),
                self.ledger.store.capture_provider_response,
            )
            # Heavy I/O, subprocesses and models are outside a database transaction.
            prepared = handler.prepare(context, request)
            checkpoint()
            for artifact in prepared.artifacts:
                self.artifacts.verify(artifact)
            with self.ledger.store.transaction():
                self.queue.assert_owned(job["id"], job["lease_token"])
                input_check(self.ledger, request)
                handler.validate(
                    ReadLedger(self.ledger), request
                )  # Rights and content scope at commit time.
                rows = []
                for record in prepared.records:
                    if record.kind not in handler.writable_kinds:
                        raise ValueError("Handler attempted a write outside its record ownership")
                    rows.append(
                        self.ledger.put(
                            record.kind,
                            record.payload,
                            record.expected_revision,
                            actor="worker:" + handler.name,
                        )
                    )
                for artifact in prepared.artifacts:
                    self.ledger.store.db.execute(
                        "INSERT OR IGNORE INTO artifact_refs VALUES(?,?,?,?)",
                        (artifact.key, artifact.sha256, artifact.size, time.time()),
                    )
                    self.ledger.store.db.execute(
                        "INSERT OR IGNORE INTO job_artifacts VALUES(?,?)", (job["id"], artifact.key)
                    )
                result = {
                    "records": [
                        {"kind": row["kind"], "id": row["id"], "revision": row["revision"]}
                        for row in rows
                    ],
                    "artifacts": [artifact.as_dict() for artifact in prepared.artifacts],
                    **prepared.summary,
                }
                self.queue.finish(job["id"], job["lease_token"], result)
        except LeaseLost:
            # No result publication; another worker/cancellation owns the state now.
            event(
                "work.lease_lost",
                run_id=request.run_id,
                job_id=job["id"],
                attempt_id=job["attempt_id"],
            )
        except Exception as exc:
            code = (
                "stale_input"
                if isinstance(exc, StaleInput)
                else "operation_ambiguous_or_budget"
                if isinstance(exc, OperationBlocked)
                else "retryable_work"
                if transient_error(exc)
                else "handler_rejected"
            )
            try:
                self.queue.fail(
                    job["id"],
                    job["lease_token"],
                    code,
                    retryable=transient_error(exc),
                    blocked=isinstance(exc, OperationBlocked),
                )
            except LeaseLost:
                pass
            except sqlite3.OperationalError as failure:
                if not transient_error(failure):
                    raise
                event("work.failure_deferred", job_id=job["id"], error_code="database_busy")
            event(
                "work.failed",
                run_id=request.run_id,
                job_id=job["id"],
                attempt_id=job["attempt_id"],
                error_code=code,
            )
        finally:
            done.set()
            if thread is not None:
                thread.join(timeout=self.settings.heartbeat_seconds + 1)
        result = self.queue.get(job["id"])
        event(
            "work.finished",
            run_id=request.run_id,
            job_id=job["id"],
            attempt_id=job["attempt_id"],
            status=result["state"],
            duration_ms=round((time.monotonic() - start) * 1000, 2),
        )
        return result

    def run(self) -> None:
        while not self.stop.is_set():
            try:
                idle = self.run_once() is None
            except sqlite3.OperationalError as exc:
                if not transient_error(exc):
                    raise
                event("work.queue_deferred", error_code="database_busy")
                idle = True
            if idle:
                self.stop.wait(self.settings.poll_seconds)
