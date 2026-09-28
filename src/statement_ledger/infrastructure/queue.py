"""At-least-once local work with fenced publication, sharing the ledger transaction."""

from __future__ import annotations

import json
import time
import uuid
from typing import Any

from statement_ledger.contracts.runtime import JobRequest
from statement_ledger.core.errors import Missing
from statement_ledger.core.util import canonical_json, digest


class LeaseLost(RuntimeError):
    pass


class RuntimeQueue:
    def __init__(self, store: Any):
        self.store = store

    @staticmethod
    def identity(request: JobRequest) -> str:
        payload = request.model_dump(mode="json", exclude={"run_id"})
        return "job-" + digest(payload)

    def submit(self, request: JobRequest) -> str:
        job_id = self.identity(request)
        with self.store.transaction():
            for artifact in request.artifacts.values():
                row = self.store.db.execute(
                    "SELECT sha256,size FROM artifact_refs WHERE key=?", (artifact.key,)
                ).fetchone()
                if row is None or tuple(row) != (artifact.sha256, artifact.size):
                    raise ValueError(
                        "Job artifacts must be registered with artifact-put before enqueue"
                    )
            event = {
                "type": "work.requested",
                "contract_version": 1,
                "job_id": job_id,
                "request": request.model_dump(mode="json"),
            }
            self.store.db.execute("INSERT INTO outbox(event) VALUES(?)", (canonical_json(event),))
            self.store.audit(
                {
                    "type": "work.requested",
                    "job_id": job_id,
                    "run_id": request.run_id,
                    "handler": request.handler,
                }
            )
        return job_id

    def _insert_job(self, request: JobRequest) -> str:
        job_id = self.identity(request)
        payload = canonical_json(request.model_dump(mode="json"))
        self.store.db.execute(
            """INSERT OR IGNORE INTO work_jobs
            (id,dedupe_key,payload,state,max_attempts,available,capability,created_at)
            VALUES(?,?,?,'pending',?,?,?,?)""",
            (
                job_id,
                job_id,
                payload,
                request.max_attempts,
                time.time(),
                request.capability,
                time.time(),
            ),
        )
        return job_id

    def dispatch(self, limit: int = 100) -> dict[str, int]:
        if not 1 <= limit <= 10000:
            raise ValueError("Invalid dispatch limit")
        dispatched = unhandled = 0
        with self.store.transaction():
            rows = self.store.db.execute(
                "SELECT sequence,event FROM outbox WHERE state='pending' ORDER BY sequence LIMIT ?",
                (limit,),
            ).fetchall()
            for row in rows:
                event = json.loads(row["event"])
                state = "unhandled"
                if event.get("type") == "work.requested":
                    request = JobRequest.model_validate(event["request"])
                    job_id = self.identity(request)
                    if event.get("job_id") != job_id:
                        raise ValueError("Outbox job identity mismatch")
                    self._insert_job(request)
                    state = "dispatched"
                    dispatched += 1
                else:
                    # Preserve unsusbcribed record events; never silently invent downstream work.
                    unhandled += 1
                self.store.db.execute(
                    "UPDATE outbox SET state=? WHERE sequence=? AND state='pending'",
                    (state, row["sequence"]),
                )
        return {"dispatched": dispatched, "unhandled": unhandled}

    def claim(
        self, capability: str = "cpu", *, lease_seconds: int = 60, clock: float | None = None
    ) -> dict[str, Any] | None:
        if capability not in {"cpu", "gpu"} or lease_seconds <= 0:
            raise ValueError("Invalid worker capability or lease")
        now = time.time() if clock is None else clock
        with self.store.transaction():
            expired = self.store.db.execute(
                "SELECT id,attempts FROM work_jobs WHERE state='running' AND lease_until<=?", (now,)
            ).fetchall()
            for row in expired:
                self.store.db.execute(
                    "UPDATE work_attempts SET status='lease_expired',finished_at=? WHERE job_id=? AND ordinal=? AND status='running'",
                    (now, row["id"], row["attempts"]),
                )
            self.store.db.execute(
                "UPDATE work_jobs SET state='failed',error_code='attempts_exhausted',lease_token=NULL,lease_until=NULL WHERE state='running' AND lease_until<=? AND attempts>=max_attempts",
                (now,),
            )
            row = self.store.db.execute(
                """SELECT * FROM work_jobs WHERE capability=? AND cancel_requested=0
                AND attempts<max_attempts AND ((state='pending' AND available<=?) OR (state='running' AND lease_until<=?))
                ORDER BY available,id LIMIT 1""",
                (capability, now, now),
            ).fetchone()
            if row is None:
                return None
            token = uuid.uuid4().hex
            attempt = "attempt-" + uuid.uuid4().hex
            ordinal = row["attempts"] + 1
            self.store.db.execute(
                "UPDATE work_jobs SET state='running',attempts=?,lease_token=?,lease_until=? WHERE id=?",
                (ordinal, token, now + lease_seconds, row["id"]),
            )
            self.store.db.execute(
                "INSERT INTO work_attempts(id,job_id,ordinal,started_at,status) VALUES(?,?,?,?,'running')",
                (attempt, row["id"], ordinal, now),
            )
            return {
                **dict(row),
                "payload": json.loads(row["payload"]),
                "attempts": ordinal,
                "attempt_id": attempt,
                "lease_token": token,
                "lease_until": now + lease_seconds,
                "state": "running",
            }

    def assert_owned(self, job_id: str, token: str, *, clock: float | None = None) -> None:
        now = time.time() if clock is None else clock
        row = self.store.db.execute(
            "SELECT 1 FROM work_jobs WHERE id=? AND state='running' AND cancel_requested=0 AND lease_token=? AND lease_until>?",
            (job_id, token, now),
        ).fetchone()
        if row is None:
            raise LeaseLost("Worker lease is expired, cancelled, or no longer owned")

    def heartbeat(
        self, job_id: str, token: str, *, lease_seconds: int = 60, clock: float | None = None
    ) -> None:
        now = time.time() if clock is None else clock
        with self.store.transaction():
            self.assert_owned(job_id, token, clock=now)
            self.store.db.execute(
                "UPDATE work_jobs SET lease_until=? WHERE id=? AND lease_token=?",
                (now + lease_seconds, job_id, token),
            )

    def finish(
        self, job_id: str, token: str, result: dict[str, Any], *, clock: float | None = None
    ) -> None:
        if not self.store.db.in_transaction:
            raise RuntimeError("Job completion must share the canonical result transaction")
        now = time.time() if clock is None else clock
        self.assert_owned(job_id, token, clock=now)
        self.store.db.execute(
            "UPDATE work_jobs SET state='succeeded',result=?,error_code=NULL,lease_token=NULL,lease_until=NULL WHERE id=?",
            (canonical_json(result), job_id),
        )
        self.store.db.execute(
            "UPDATE work_attempts SET status='succeeded',finished_at=?,duration_ms=(?-started_at)*1000 WHERE job_id=? AND status='running'",
            (now, now, job_id),
        )
        self.store.audit({"type": "work.completed", "job_id": job_id})

    def fail(
        self,
        job_id: str,
        token: str,
        error_code: str,
        *,
        retryable: bool = False,
        blocked: bool = False,
        clock: float | None = None,
    ) -> None:
        if not error_code.replace("_", "").isalnum():
            raise ValueError("Only safe error codes may be persisted")
        now = time.time() if clock is None else clock
        with self.store.transaction():
            self.assert_owned(job_id, token, clock=now)
            row = self.store.db.execute(
                "SELECT attempts,max_attempts FROM work_jobs WHERE id=?", (job_id,)
            ).fetchone()
            state = (
                "blocked"
                if blocked
                else "pending"
                if retryable and row["attempts"] < row["max_attempts"]
                else "failed"
            )
            delay = min(300, 2 ** row["attempts"])
            self.store.db.execute(
                "UPDATE work_jobs SET state=?,available=?,error_code=?,lease_token=NULL,lease_until=NULL WHERE id=?",
                (state, now + delay, error_code[:100], job_id),
            )
            self.store.db.execute(
                "UPDATE work_attempts SET status=?,finished_at=?,error_code=?,duration_ms=(?-started_at)*1000 WHERE job_id=? AND status='running'",
                (state, now, error_code[:100], now, job_id),
            )
            self.store.audit(
                {"type": "work.failed", "job_id": job_id, "status": state, "error_code": error_code}
            )

    def cancel(self, job_id: str) -> None:
        with self.store.transaction():
            row = self.store.db.execute(
                "SELECT state FROM work_jobs WHERE id=?", (job_id,)
            ).fetchone()
            if row is None:
                pending = self.store.db.execute(
                    "SELECT sequence,event FROM outbox WHERE state='pending' AND json_extract(event,'$.job_id')=? ORDER BY sequence LIMIT 1",
                    (job_id,),
                ).fetchone()
                if pending is None:
                    raise Missing("work_job:" + job_id)
                request = JobRequest.model_validate(json.loads(pending["event"])["request"])
                if self.identity(request) != job_id:
                    raise ValueError("Pending job identity mismatch")
                self._insert_job(request)
                self.store.db.execute(
                    "UPDATE outbox SET state='dispatched' WHERE sequence=?", (pending["sequence"],)
                )
                row = {"state": "pending"}
            if row["state"] in {"succeeded", "failed", "cancelled"}:
                return
            self.store.db.execute(
                "UPDATE work_jobs SET cancel_requested=1,state='cancelled',lease_token=NULL,lease_until=NULL WHERE id=?",
                (job_id,),
            )
            self.store.db.execute(
                "UPDATE work_attempts SET status='cancelled',finished_at=? WHERE job_id=? AND status='running'",
                (time.time(), job_id),
            )
            self.store.audit({"type": "work.cancelled", "job_id": job_id})

    def get(self, job_id: str) -> dict[str, Any]:
        row = self.store.db.execute("SELECT * FROM work_jobs WHERE id=?", (job_id,)).fetchone()
        if row is None:
            raise Missing("work_job:" + job_id)
        result = dict(row)
        result["payload"] = json.loads(result["payload"])
        result["result"] = json.loads(result["result"]) if result["result"] else None
        result.pop("lease_token", None)
        return result

    def list(self, *, limit: int = 100) -> list[dict[str, Any]]:
        if not 1 <= limit <= 1000:
            raise ValueError("Invalid queue listing limit")
        return [
            self.get(row[0])
            for row in self.store.db.execute(
                "SELECT id FROM work_jobs ORDER BY created_at,id LIMIT ?", (limit,)
            ).fetchall()
        ]
