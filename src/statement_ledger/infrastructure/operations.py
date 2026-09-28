"""Reserve before spending. Unknown remote outcomes require operator reconciliation."""

from __future__ import annotations

import json
import time
import uuid
from typing import Any

from statement_ledger.core.errors import Missing
from statement_ledger.core.util import canonical_json, digest


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
            # Every reservation is a distinct historical attempt, including known-unsent ones.
            if self.store.db.execute(
                "SELECT 1 FROM provider_operations WHERE id=?", (operation_id,)
            ).fetchone():
                raise OperationBlocked(
                    "Operation ID already exists; historical attempts are immutable"
                )
            history = self._history(request_hash, provider)
            if any(row["state"] in {"started", "unknown"} for row in history):
                raise OperationBlocked(
                    "Reconcile outstanding remote outcomes before another attempt"
                )
            authorization = self._pending_authorization(request_hash, provider)
            if any(row["state"] != "cancelled" for row in history) and authorization is None:
                raise OperationBlocked(
                    "Request already recorded; recover its receipt or explicitly authorize one new attempt"
                )
            if authorization is not None and authorization["basis_sha256"] != digest(history):
                raise OperationBlocked(
                    "Operation history changed; owner must renew retry authorization"
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
            if authorization is not None:
                self.store.db.execute(
                    "UPDATE provider_retry_authorizations SET state='consumed',consumed_by=?,finished_at=? WHERE id=? AND state='issued'",
                    (operation_id, time.time(), authorization["id"]),
                )
                self.store.audit(
                    {
                        "type": "provider.retry_authorization_consumed",
                        "authorization_id": authorization["id"],
                        "operation_id": operation_id,
                        "request_hash": request_hash,
                        "actor": authorization["actor"],
                        "reason": authorization["reason"],
                    }
                )
            self.store.audit(
                {
                    "type": "provider.operation_reserved",
                    "operation_id": operation_id,
                    "request_hash": request_hash,
                    "estimated_micro_usd": estimate_micro_usd,
                }
            )

    def get(self, operation_id: str) -> dict[str, Any]:
        row = self.store.db.execute(
            "SELECT * FROM provider_operations WHERE id=?", (operation_id,)
        ).fetchone()
        if row is None:
            raise Missing("provider_operation:" + operation_id)
        result = dict(row)
        result["usage"] = json.loads(result["usage"]) if result["usage"] else None
        return result

    def _history(self, request_hash: str, provider: str) -> list[dict[str, Any]]:
        return [
            dict(row)
            for row in self.store.db.execute(
                "SELECT * FROM provider_operations WHERE request_hash=? AND provider=? ORDER BY started_at,id",
                (request_hash, provider),
            )
        ]

    def _pending_authorization(self, request_hash: str, provider: str) -> dict[str, Any] | None:
        row = self.store.db.execute(
            "SELECT * FROM provider_retry_authorizations WHERE request_hash=? AND provider=? AND state='issued'",
            (request_hash, provider),
        ).fetchone()
        return dict(row) if row is not None else None

    def retry_authorized(self, request_hash: str, provider: str) -> bool:
        # A hint for cache routing only. begin() checks and consumes atomically.
        return self._pending_authorization(request_hash, provider) is not None

    @staticmethod
    def validate_owner_action(actor: str, reason: str) -> None:
        if not actor.strip() or len(actor) > 180 or not reason.strip() or len(reason) > 2000:
            raise ValueError("Owner action requires an actor and a bounded nonblank reason")

    def authorize_retry(self, operation_id: str, *, actor: str, reason: str) -> dict[str, Any]:
        """Authorize exactly one reservation after reconciliation, not a call or a job requeue."""
        self.validate_owner_action(actor, reason)
        with self.store.transaction():
            operation = self.get(operation_id)
            history = self._history(operation["request_hash"], operation["provider"])
            if operation["state"] != "completed" or any(
                row["state"] in {"started", "unknown"} for row in history
            ):
                raise OperationBlocked("Reconcile remote outcomes before authorizing a new attempt")
            if self._pending_authorization(operation["request_hash"], operation["provider"]):
                raise OperationBlocked(
                    "An unused authorization already exists; revoke it before replacing"
                )
            authorization_id = "retry-" + uuid.uuid4().hex
            self.store.db.execute(
                "INSERT INTO provider_retry_authorizations(id,request_hash,provider,basis_sha256,actor,reason,authorized_at,state) VALUES(?,?,?,?,?,?,?,'issued')",
                (
                    authorization_id,
                    operation["request_hash"],
                    operation["provider"],
                    digest(history),
                    actor,
                    reason,
                    time.time(),
                ),
            )
            self.store.audit(
                {
                    "type": "provider.retry_authorized",
                    "authorization_id": authorization_id,
                    "operation_id": operation_id,
                    "request_hash": operation["request_hash"],
                    "provider": operation["provider"],
                    "actor": actor,
                    "reason": reason,
                    "maximum_new_attempts": 1,
                }
            )
            return {
                "authorization_id": authorization_id,
                "request_hash": operation["request_hash"],
                "maximum_new_attempts": 1,
                "automatic_retry": False,
            }

    def revoke_retry(self, authorization_id: str, *, actor: str, reason: str) -> None:
        self.validate_owner_action(actor, reason)
        with self.store.transaction():
            cursor = self.store.db.execute(
                "UPDATE provider_retry_authorizations SET state='revoked',finished_at=? WHERE id=? AND state='issued'",
                (time.time(), authorization_id),
            )
            if cursor.rowcount != 1:
                raise OperationBlocked("Authorization is absent or no longer unused")
            self.store.audit(
                {
                    "type": "provider.retry_authorization_revoked",
                    "authorization_id": authorization_id,
                    "actor": actor,
                    "reason": reason,
                }
            )

    def authorizations(self) -> list[dict[str, Any]]:
        return [
            dict(row)
            for row in self.store.db.execute(
                "SELECT * FROM provider_retry_authorizations ORDER BY authorized_at,id"
            )
        ]

    def attach_decision(
        self, operation_id: str, payload: dict[str, Any], *, actor: str, reason: str
    ) -> None:
        """Internal: caller validates the retained receipt and writes the record in this transaction."""
        self.validate_owner_action(actor, reason)
        with self.store.transaction():
            operation = self.get(operation_id)
            if operation["state"] != "completed" or operation["request_hash"] != payload.get(
                "request_hash"
            ):
                raise OperationBlocked(
                    "Only a completed matching operation can receive a recovered decision"
                )
            if any(
                row["state"] in {"started", "unknown"}
                for row in self._history(operation["request_hash"], operation["provider"])
            ):
                raise OperationBlocked(
                    "Reconcile outstanding operations before recovering a decision"
                )
            usage = operation["usage"] or {}
            if usage.get("decision") and usage["decision"] != payload:
                raise OperationBlocked("Operation already has a different recovered decision")
            self.store.db.execute(
                "UPDATE provider_operations SET usage=? WHERE id=?",
                (
                    canonical_json(
                        {**usage, "decision": payload, "receipt_ids": payload["receipt_ids"]}
                    ),
                    operation_id,
                ),
            )
            pending = self._pending_authorization(operation["request_hash"], operation["provider"])
            if pending is not None:
                self.revoke_retry(
                    pending["id"],
                    actor=actor,
                    reason="Recovered retained decision: " + reason[:1900],
                )
            self.store.audit(
                {
                    "type": "provider.decision_recovered_by_owner",
                    "operation_id": operation_id,
                    "decision_id": payload["id"],
                    "receipt_ids": payload["receipt_ids"],
                    "request_hash": operation["request_hash"],
                    "actor": actor,
                    "reason": reason,
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
            "SELECT state,usage FROM provider_operations WHERE request_hash=? AND provider=? AND state!='cancelled' ORDER BY started_at DESC,id DESC",
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

    def reconcile(
        self, operation_id: str, *, actual_micro_usd: int, evidence: str, actor: str = "local-owner"
    ) -> None:
        self.validate_owner_action(actor, evidence)
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
                    "actor": actor,
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
