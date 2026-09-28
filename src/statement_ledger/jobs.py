"""Standalone durable task ledger. Task execution is explicit, not an autonomous crawler.

Leases use compare-and-swap tokens; expired workers cannot complete a newly leased
job. One queue DB may be shared by local processes. This is not a distributed SLA.
"""

import json
import sqlite3
import time
import uuid

from statement_ledger.core.util import canonical_json, digest


class JobQueue:
    def __init__(self, path):
        self.db = sqlite3.connect(str(path), isolation_level=None, timeout=30)
        self.db.row_factory = sqlite3.Row
        self.db.executescript("""CREATE TABLE IF NOT EXISTS jobs(
        id TEXT PRIMARY KEY,dedupe_key TEXT UNIQUE NOT NULL,payload TEXT NOT NULL,
        state TEXT NOT NULL,attempts INTEGER NOT NULL,max_attempts INTEGER NOT NULL,
        available REAL NOT NULL,lease_until REAL,lease_token TEXT,result TEXT,error TEXT);
        CREATE INDEX IF NOT EXISTS jobs_ready ON jobs(state,available);""")

    def close(self):
        self.db.close()

    def enqueue(self, payload: dict, *, key: str | None = None, max_attempts: int = 3) -> str:
        if not 1 <= max_attempts <= 10:
            raise ValueError("max_attempts must be 1..10")
        dedupe = key or digest(payload)
        ident = str(uuid.uuid4())
        self.db.execute(
            "INSERT OR IGNORE INTO jobs VALUES (?,?,?,'pending',0,?,?,NULL,NULL,NULL,NULL)",
            (ident, dedupe, canonical_json(payload), max_attempts, time.time()),
        )
        row = self.db.execute(
            "SELECT id,payload FROM jobs WHERE dedupe_key=?", (dedupe,)
        ).fetchone()
        if row["payload"] != canonical_json(payload):
            raise ValueError("Idempotency key reused with different payload")
        return row["id"]

    def claim(self, *, lease_seconds: int = 60, clock: float | None = None) -> dict | None:
        if lease_seconds < 1:
            raise ValueError("lease_seconds must be positive")
        now = time.time() if clock is None else clock
        self.db.execute("BEGIN IMMEDIATE")
        try:
            self.db.execute(
                "UPDATE jobs SET state='failed',error='Lease attempts exhausted' WHERE state='running' AND lease_until<=? AND attempts>=max_attempts",
                (now,),
            )
            row = self.db.execute(
                "SELECT * FROM jobs WHERE ((state='pending' AND available<=?) OR (state='running' AND lease_until<=?)) AND attempts<max_attempts ORDER BY available,id LIMIT 1",
                (now, now),
            ).fetchone()
            if not row:
                self.db.commit()
                return None
            token = str(uuid.uuid4())
            self.db.execute(
                "UPDATE jobs SET state='running',attempts=attempts+1,lease_until=?,lease_token=? WHERE id=?",
                (now + lease_seconds, token, row["id"]),
            )
            self.db.commit()
            out = dict(row)
            out.update(
                lease_token=token,
                state="running",
                attempts=row["attempts"] + 1,
                lease_until=now + lease_seconds,
            )
            out["payload"] = json.loads(out["payload"])
            return out
        except BaseException:
            self.db.rollback()
            raise

    def finish(self, job_id: str, token: str, result: dict, *, clock: float | None = None):
        now = time.time() if clock is None else clock
        cur = self.db.execute(
            "UPDATE jobs SET state='succeeded',result=?,error=NULL,lease_until=NULL,lease_token=NULL WHERE id=? AND state='running' AND lease_token=? AND lease_until>?",
            (canonical_json(result), job_id, token, now),
        )
        if cur.rowcount != 1:
            raise ValueError("Job lease is no longer owned")

    def fail(self, job_id: str, token: str, error_code: str, *, clock: float | None = None):
        now = time.time() if clock is None else clock
        # Caller passes a safe error class/code, never raw credential-bearing URLs.
        cur = self.db.execute(
            "UPDATE jobs SET state=CASE WHEN attempts>=max_attempts THEN 'failed' ELSE 'pending' END,available=?,error=?,lease_until=NULL,lease_token=NULL WHERE id=? AND state='running' AND lease_token=? AND lease_until>?",
            (now + 30, error_code[:100], job_id, token, now),
        )
        if cur.rowcount != 1:
            raise ValueError("Job lease is no longer owned")

    def list(self):
        return [dict(r) for r in self.db.execute("SELECT * FROM jobs ORDER BY available,id")]
