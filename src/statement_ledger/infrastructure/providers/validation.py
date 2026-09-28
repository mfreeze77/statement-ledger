from __future__ import annotations

from statement_ledger.core.policy import PolicyError
from statement_ledger.core.util import digest


def validate_decision_run(ledger, payload, ref):
    from statement_ledger.infrastructure.providers.jev import validate_questions, validate_response

    validate_questions(payload["questions"])
    for b in payload["bindings"]:
        ref(b["kind"], b["id"])
        if ledger.store.get(b["kind"], b["id"])["revision"] != b["revision"]:
            raise PolicyError("Decision binding revision mismatch")
    for rid in payload["receipt_ids"]:
        receipt = ledger.store.provider_receipt(rid)
        if receipt["request_hash"] != payload["request_hash"]:
            raise PolicyError("Provider receipt request mismatch")
        meta = receipt["request_metadata"]
        if (
            meta["model"] != payload["model_requested"]
            or meta["purpose"] != payload["purpose"]
            or meta["question_version"] != payload["question_version"]
            or (digest(meta) != payload["request_hash"])
            or (meta["bindings"] != payload["bindings"])
            or (meta["questions"] != payload["questions"])
            or (meta["input_ids"] != payload["input_ids"])
            or (digest(meta["state"]) != payload["state_sha256"])
        ):
            raise PolicyError("Provider receipt binding mismatch")
    if payload["status"] == "available":
        if not payload["receipt_ids"]:
            raise PolicyError("Available decision requires a captured provider response")
        from statement_ledger.infrastructure.providers.jev import strict_loads

        receipt = ledger.store.provider_receipt(payload["receipt_ids"][-1])
        if receipt["http_status"] != 200 or receipt["truncated"]:
            raise PolicyError("Available decision needs an intact HTTP 200 receipt")
        validated = validate_response(
            strict_loads(receipt["body"]), payload["questions"], payload["model_requested"]
        )
        if (
            payload["answers"] != validated["answers"]
            or payload["warnings"] != validated["warnings"]
            or payload["model_resolved"] != validated["model_resolved"]
            or (payload["usage"] != validated["usage"])
        ):
            raise PolicyError("Decision differs from its captured response")
