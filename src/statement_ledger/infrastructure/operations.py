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
                "SELECT state,request_hash FROM provider_operations WHERE id=?", (operation_id,)
            ).fetchone()
            if existing is not None:
                raise OperationBlocked(
                    "Operation already recorded; recover its captured response or reconcile it before retrying"
                )
            reserved = self.store.db.execute(
                "SELECT COALESCE(SUM(COALESCE(actual_micro_usd,estimated_micro_usd)),0) FROM provider_operations WHERE state!='cancelled'"
            ).fetchone()[0]
            if reserved + estimate_micro_usd > budget_micro_usd:
                raise OperationBlocked("Remote budget would be exceeded")
            self.store.db.execute(
                "INSERT INTO provider_operations(id,request_hash,provider,state,estimated_micro_usd,started_at,cost_status) VALUES(?,?,?,'started',?,?,'estimated')",
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
