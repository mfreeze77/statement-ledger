"""Explicit local-owner recovery. No credentials, transport, or automatic retries."""

from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Any

from statement_ledger.contracts.models import now
from statement_ledger.core.errors import Missing
from statement_ledger.core.util import digest
from statement_ledger.infrastructure.operations import OperationBlocked, OperationJournal
from statement_ledger.infrastructure.providers.jev import (
    ENDPOINT,
    VALIDATOR_VERSION,
    authorize_bindings,
    strict_loads,
    validate_questions,
    validate_response,
)


def recover_jev_operation(
    ledger: Any, operation_id: str, receipt_id: str, *, actor: str, reason: str
) -> dict[str, Any]:
    """Reparse an existing receipt, preserving its timestamp and source bindings.

    Cost reconciliation must happen first. This attaches a historical advisory record,
    not a reviewed finding. Cache eligibility still applies when a later job tries reuse.
    """
    journal = OperationJournal(ledger.store)
    journal.validate_owner_action(actor, reason)
    with ledger.store.transaction():
        operation = journal.get(operation_id)
        if operation["provider"] != "typesafe" or operation["state"] != "completed":
            raise OperationBlocked("Reconcile a TypeSafe operation before recovering its receipt")
        receipt = ledger.store.provider_receipt(receipt_id)
        journal.require_receipt_binding(operation_id, receipt_id)
        metadata = receipt["request_metadata"]
        expected = {
            "purpose",
            "question_version",
            "state",
            "questions",
            "input_ids",
            "bindings",
            "endpoint",
            "model",
            "validator",
        }
        if (
            set(metadata) != expected
            or metadata["endpoint"] != ENDPOINT
            or metadata["validator"] != VALIDATOR_VERSION
            or receipt["request_hash"] != operation["request_hash"]
            or digest(metadata) != operation["request_hash"]
        ):
            raise ValueError("Receipt does not match the recorded provider request")
        if (
            receipt["http_status"] != 200
            or receipt["truncated"]
            or hashlib.sha256(receipt["body"]).hexdigest() != receipt["body_sha256"]
        ):
            raise ValueError("Recovery requires an intact, checksum-verified HTTP 200 receipt")
        captured = datetime.fromisoformat(receipt["captured_at"])
        if captured.tzinfo is None or captured > now():
            raise ValueError("Receipt capture time must be timezone-aware and not in the future")
        retained_ids = (operation["usage"] or {}).get("receipt_ids")
        if retained_ids and receipt_id not in retained_ids:
            raise ValueError("Receipt is not one of the operation's retained receipts")
        if not metadata["bindings"]:
            raise ValueError("Recovery requires source-bound inputs")
        authorize_bindings(ledger, metadata["bindings"])
        validate_questions(metadata["questions"])
        result = validate_response(
            strict_loads(receipt["body"]), metadata["questions"], metadata["model"]
        )
        decision_id = "decision-recovered-" + digest([operation_id, receipt_id])
        payload = {
            "id": decision_id,
            "purpose": metadata["purpose"],
            "request_hash": operation["request_hash"],
            "model_requested": metadata["model"],
            "question_version": metadata["question_version"],
            "questions": metadata["questions"],
            "state_sha256": digest(metadata["state"]),
            "bindings": metadata["bindings"],
            "input_ids": metadata["input_ids"],
            "captured_at": receipt["captured_at"],
            "status": "available",
            "error_code": None,
            "latency_ms": None,
            "receipt_ids": [receipt_id],
            **result,
        }
        try:
            revision = ledger.store.get("decision_run", decision_id)["revision"]
        except Missing:
            revision = 0
        row = ledger.put("decision_run", payload, revision, actor=actor)
        # Same transaction: a rejected attachment rolls the canonical write back too.
        journal.attach_decision(operation_id, row["payload"], actor=actor, reason=reason)
        return {
            "operation_id": operation_id,
            "decision_id": decision_id,
            "revision": row["revision"],
            "provider_calls": 0,
            "automatic_retry": False,
        }
