"""Reserve before spending. Unknown remote outcomes require operator reconciliation."""

from __future__ import annotations

import json
import time
from typing import Any

from statement_ledger.core.util import canonical_json


class OperationBlocked(RuntimeError):
    pass


class OperationJournal:
    def __init__(self, store: Any):
        self.store = store

    def begin(
        self,
        operation_id: str,
        request_hash: str,
        provider: str,
        *,
        estimate_micro_usd: int,
        budget_micro_usd: int,
    ) -> None:
        if (
            type(estimate_micro_usd) is not int
            or type(budget_micro_usd) is not int
            or estimate_micro_usd <= 0
            or budget_micro_usd <= 0
        ):
            raise OperationBlocked("A positive explicit remote budget and estimate are required")
        with self.store.transaction():
            existing = self.store.db.execute(
                "SELECT id,state,request_hash,provider FROM provider_operations WHERE id=? OR (request_hash=? AND provider=? AND state!='cancelled')",
                (operation_id, request_hash, provider),
            ).fetchall()
            if any(
                row["state"] != "cancelled"
                or row["request_hash"] != request_hash
                or row["provider"] != provider
                for row in existing
            ):
                raise OperationBlocked(
                    "Request already recorded; recover its captured decision or reconcile the operation"
                )
            reserved = self.store.db.execute(
                "SELECT COALESCE(SUM(COALESCE(actual_micro_usd,estimated_micro_usd)),0) FROM provider_operations WHERE state!='cancelled'"
            ).fetchone()[0]
            if reserved + estimate_micro_usd > budget_micro_usd:
                raise OperationBlocked("Remote budget would be exceeded")
            self.store.db.execute(
                "INSERT INTO provider_operations(id,request_hash,provider,state,estimated_micro_usd,started_at,cost_status) VALUES(?,?,?,'started',?,?,'estimated') ON CONFLICT(id) DO UPDATE SET state='started',estimated_micro_usd=excluded.estimated_micro_usd,started_at=excluded.started_at,finished_at=NULL,actual_micro_usd=NULL,usage=NULL,cost_status='estimated'",
                (operation_id, request_hash, provider, estimate_micro_usd, time.time()),
            )
            self.store.audit(
                {
                    "type": "provider.operation_reserved",
                    "operation_id": operation_id,
                    "request_hash": request_hash,
                    "estimated_micro_usd": estimate_micro_usd,
                }
            )

    def complete(
        self, operation_id: str, usage: dict[str, Any], *, actual_micro_usd: int | None = None
    ) -> None:
        if actual_micro_usd is not None and (
            type(actual_micro_usd) is not int or actual_micro_usd < 0
        ):
            raise ValueError("Actual cost must be a nonnegative integer or unknown")
        with self.store.transaction():
            cursor = self.store.db.execute(
                "UPDATE provider_operations SET state='completed',usage=?,actual_micro_usd=?,finished_at=?,cost_status=? WHERE id=? AND state='started'",
                (
                    canonical_json(usage),
                    actual_micro_usd,
                    time.time(),
                    "actual" if actual_micro_usd is not None else "unknown",
                    operation_id,
                ),
            )
            if cursor.rowcount != 1:
                raise OperationBlocked("Operation is not awaiting completion")

    def unknown(self, operation_id: str) -> None:
        with self.store.transaction():
            self.store.db.execute(
                "UPDATE provider_operations SET state='unknown',cost_status='unknown',finished_at=? WHERE id=? AND state='started'",
                (time.time(), operation_id),
            )

    def cancel_unsent(self, operation_id: str) -> None:
        """Only the owning handler before network submission may declare zero external effect."""
        with self.store.transaction():
            cursor = self.store.db.execute(
                "UPDATE provider_operations SET state='cancelled',cost_status='actual',actual_micro_usd=0,finished_at=? WHERE id=? AND state='started'",
                (time.time(), operation_id),
            )
            if cursor.rowcount != 1:
                raise OperationBlocked("Unsent operation is no longer owned")
            self.store.audit(
                {"type": "provider.operation_cancelled_unsent", "operation_id": operation_id}
            )

    def recover_decision(self, request_hash: str, provider: str) -> dict[str, Any] | None:
        rows = self.store.db.execute(
            "SELECT state,usage FROM provider_operations WHERE request_hash=? AND provider=? AND state!='cancelled' ORDER BY started_at,id",
            (request_hash, provider),
        ).fetchall()
        if any(row["state"] in {"started", "unknown"} for row in rows):
            raise OperationBlocked(
                "Unresolved remote outcome; automatic repeat spending is forbidden"
            )
        for row in rows:
            usage = json.loads(row["usage"]) if row["usage"] else {}
            payload = usage.get("decision")
            if isinstance(payload, dict) and payload.get("request_hash") == request_hash:
                return payload
        return None

    def reconcile(self, operation_id: str, *, actual_micro_usd: int, evidence: str) -> None:
        if not evidence.strip() or type(actual_micro_usd) is not int or actual_micro_usd < 0:
            raise ValueError("Reconciliation requires documented nonnegative actual cost")
        with self.store.transaction():
            cursor = self.store.db.execute(
                "UPDATE provider_operations SET state='completed',cost_status='actual',actual_micro_usd=?,finished_at=? WHERE id=? AND state IN ('unknown','started','completed')",
                (actual_micro_usd, time.time(), operation_id),
            )
            if cursor.rowcount != 1:
                raise KeyError(operation_id)
            self.store.audit(
                {
                    "type": "provider.operation_reconciled",
                    "operation_id": operation_id,
                    "actual_micro_usd": actual_micro_usd,
                    "operator_evidence": evidence,
                }
            )

    def list(self) -> list[dict[str, Any]]:
        rows = [
            dict(row)
            for row in self.store.db.execute(
                "SELECT * FROM provider_operations ORDER BY started_at,id"
            )
        ]
        for row in rows:
            row["usage"] = json.loads(row["usage"]) if row["usage"] else None
        return rows
