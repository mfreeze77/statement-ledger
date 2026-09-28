"""Shared CLI/runtime commands. All canonical writes go through the composition root."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import platform
import shutil
import signal
import sqlite3
import subprocess
import time
from pathlib import Path
from typing import Any

from statement_ledger.application.handlers import handlers
from statement_ledger.application.ledger import Ledger
from statement_ledger.contracts.runtime import JobRequest
from statement_ledger.infrastructure.artifacts import LocalArtifactStore
from statement_ledger.infrastructure.backup import backup, restore
from statement_ledger.infrastructure.logging import configure_logging
from statement_ledger.infrastructure.migrations import migrate, wal_is_fixed
from statement_ledger.infrastructure.operations import OperationJournal
from statement_ledger.infrastructure.queue import RuntimeQueue
from statement_ledger.infrastructure.settings import Settings
from statement_ledger.infrastructure.sqlite_store import Store
from statement_ledger.infrastructure.worker import Worker, input_check

COMMANDS = frozenset(
    {
        "migrate",
        "doctor",
        "config",
        "artifact-put",
        "enqueue",
        "worker",
        "jobs",
        "dispatch",
        "cancel-job",
        "requeue-job",
        "backup-workspace",
        "restore-workspace",
        "operations",
        "reconcile-operation",
        "authorize-operation-retry",
        "recover-operation-decision",
        "revoke-operation-retry",
    }
)


def add_commands(subparsers: Any) -> None:
    parser = subparsers.add_parser("migrate")
    parser.add_argument("--legacy-jobs", type=Path)
    parser = subparsers.add_parser("doctor")
    parser.add_argument("--gpu", action="store_true")
    subparsers.add_parser("config")
    parser = subparsers.add_parser("artifact-put")
    parser.add_argument("file", type=Path)
    parser = subparsers.add_parser("enqueue")
    parser.add_argument("file", type=Path)
    parser = subparsers.add_parser("worker")
    parser.add_argument("--once", action="store_true")
    subparsers.add_parser("jobs")
    subparsers.add_parser("dispatch")
    parser = subparsers.add_parser("cancel-job")
    parser.add_argument("job_id")
    parser = subparsers.add_parser("requeue-job")
    parser.add_argument("job_id")
    parser.add_argument("--reason", required=True)
    parser.add_argument("--additional-attempts", type=int, default=1)
    parser = subparsers.add_parser("backup-workspace")
    parser.add_argument("destination", type=Path)
    parser = subparsers.add_parser("restore-workspace")
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    subparsers.add_parser("operations")
    parser = subparsers.add_parser("reconcile-operation")
    parser.add_argument("operation_id")
    parser.add_argument("--actual-micro-usd", type=int, required=True)
    parser.add_argument("--evidence", required=True)
    parser = subparsers.add_parser("authorize-operation-retry")
    parser.add_argument("operation_id")
    parser.add_argument("--reason", required=True)
    parser = subparsers.add_parser("recover-operation-decision")
    parser.add_argument("operation_id")
    parser.add_argument("--receipt-id", required=True)
    parser.add_argument("--reason", required=True)
    parser = subparsers.add_parser("revoke-operation-retry")
    parser.add_argument("authorization_id")
    parser.add_argument("--reason", required=True)


def doctor(settings: Settings, *, gpu: bool = False) -> dict[str, Any]:
    packages = {}
    for name in ("statement-ledger", "pydantic", "fastapi", "httpx", "uvicorn", "uv"):
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = "not_installed"
    ffmpeg = shutil.which("ffmpeg")
    result: dict[str, Any] = {
        "python": platform.python_version(),
        "sqlite": sqlite3.sqlite_version,
        "sqlite_wal_fixed": wal_is_fixed(),
        "journal_mode": settings.journal_mode,
        "packages": packages,
        "ffmpeg": None,
        "gpu_requested": gpu,
        "schema_ready": False,
        "provider_calls": False,
    }
    if ffmpeg:
        result["ffmpeg"] = subprocess.run(
            [ffmpeg, "-version"], capture_output=True, text=True, check=True, timeout=15
        ).stdout.splitlines()[0]
    lock = Path(__file__).resolve().parents[3] / "uv.lock"
    result["lock_sha256"] = (
        hashlib.sha256(lock.read_bytes()).hexdigest() if lock.is_file() else None
    )
    try:
        store = Store(settings.database, journal_mode=settings.journal_mode)
        store.close()
        result["schema_ready"] = True
    except (RuntimeError, sqlite3.Error):
        result["schema_error"] = "migration_or_runtime_required"
    if gpu:
        try:
            import torch

            result["gpu_available"] = bool(torch.cuda.is_available())
            result["torch_version"] = torch.__version__
            result["cuda_version"] = torch.version.cuda
            result["device"] = torch.cuda.get_device_name(0) if result["gpu_available"] else None
        except ImportError:
            result["gpu_available"] = False
            result["gpu_error"] = "optional_gpu_environment_not_installed"
    return result


def execute(args: argparse.Namespace, settings: Settings) -> dict[str, Any]:
    if args.command == "config":
        return {
            "settings": settings.model_dump(mode="json"),
            "execution_hash": settings.execution_hash(),
            "secrets": "references_only",
        }
    if args.command == "doctor":
        return doctor(settings, gpu=args.gpu)
    settings.prepare_directories()
    if args.command == "migrate":
        old_default = settings.data_root / "ledger.sqlite3"
        if old_default.exists() and old_default.resolve() != settings.database.resolve():
            raise ValueError(
                "Legacy ledger.sqlite3 found; set SL_DB_PATH to it or perform an explicit verified restore"
            )
        legacy = args.legacy_jobs or settings.legacy_jobs_path
        if legacy is None:
            # Fail on known legacy sidecar locations; arbitrary custom locations must be supplied.
            for candidate in (settings.data_root / "jobs.db", settings.data_root / "jobs.sqlite3"):
                if candidate.exists():
                    legacy = candidate
                    break
        return migrate(settings.database, legacy_jobs_path=legacy)
    if args.command == "backup-workspace":
        return backup(settings, args.destination)
    if args.command == "restore-workspace":
        return restore(args.source, args.destination)
    store = Store(settings.database, journal_mode=settings.journal_mode)
    try:
        ledger = Ledger(store)
        ledger.settings = settings
        queue = RuntimeQueue(store)
        if args.command == "artifact-put":
            artifacts = LocalArtifactStore(
                settings.artifacts, max_bytes=settings.max_artifact_bytes
            )
            with args.file.open("rb") as stream:
                artifact = artifacts.put(stream)
            with store.transaction():
                store.db.execute(
                    "INSERT OR IGNORE INTO artifact_refs VALUES(?,?,?,?)",
                    (artifact.key, artifact.sha256, artifact.size, time.time()),
                )
                store.audit(
                    {
                        "type": "artifact.registered",
                        "key": artifact.key,
                        "sha256": artifact.sha256,
                        "size": artifact.size,
                    }
                )
            return artifact.as_dict()
        if args.command == "enqueue":
            request = JobRequest.model_validate_json(args.file.read_text(encoding="utf-8"))
            handler = handlers().get(request.handler)
            if handler is None or handler.capability != request.capability:
                raise ValueError("Unknown or incompatible handler")
            input_check(ledger, request)
            handler.validate(ledger, request)
            if request.config_sha256 != settings.execution_hash():
                raise ValueError("Use the current execution_hash reported by config")
            return {**queue.submit_with_status(request), "run_id": request.run_id}
        if args.command == "dispatch":
            return queue.dispatch()
        if args.command == "jobs":
            return {"jobs": queue.list()}
        if args.command == "cancel-job":
            queue.cancel(args.job_id)
            return queue.get(args.job_id)
        if args.command == "requeue-job":
            return queue.requeue(
                args.job_id, reason=args.reason, additional_attempts=args.additional_attempts
            )
        if args.command == "operations":
            return {
                "operations": OperationJournal(store).list(),
                "retry_authorizations": OperationJournal(store).authorizations(),
            }
        if args.command == "reconcile-operation":
            OperationJournal(store).reconcile(
                args.operation_id, actual_micro_usd=args.actual_micro_usd, evidence=args.evidence
            )
            return {"reconciled": args.operation_id, "automatic_retry": False}
        if args.command == "authorize-operation-retry":
            return OperationJournal(store).authorize_retry(
                args.operation_id, actor="local-owner", reason=args.reason
            )
        if args.command == "recover-operation-decision":
            from statement_ledger.application.operation_recovery import recover_jev_operation

            return recover_jev_operation(
                ledger, args.operation_id, args.receipt_id, actor="local-owner", reason=args.reason
            )
        if args.command == "revoke-operation-retry":
            OperationJournal(store).revoke_retry(
                args.authorization_id, actor="local-owner", reason=args.reason
            )
            return {"revoked": args.authorization_id, "automatic_retry": False}
        if args.command == "worker":
            configure_logging(settings.log_level)
            worker = Worker(ledger, settings, handlers())
            if args.once:
                return {"job": worker.run_once()}
            previous = {}
            for sig in (signal.SIGINT, signal.SIGTERM):
                previous[sig] = signal.signal(sig, lambda *_: worker.stop.set())
            try:
                worker.run()
            finally:
                for sig, value in previous.items():
                    signal.signal(sig, value)
            return {"stopped": True}
        raise ValueError("Unknown runtime command")
    finally:
        store.close()
