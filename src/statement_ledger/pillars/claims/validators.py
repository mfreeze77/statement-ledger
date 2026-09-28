from __future__ import annotations

from datetime import datetime

from statement_ledger.core.policy import PolicyError


def validate_proposition(ledger, payload, ref):
    for oid in payload["seed_observation_ids"]:
        ref("observation", oid)


def validate_occurrence(ledger, payload, ref):
    utterance = ref("utterance", payload["utterance_id"])
    ref("proposition", payload["proposition_id"])
    if payload["extraction_reviewed_by"] and (
        utterance["status"] != "accepted" or not payload["extraction_rationale"]
    ):
        raise PolicyError("Reviewed extraction requires accepted utterance and rationale")


def validate_claim_family(ledger, payload, ref):
    if len(set(payload["proposition_ids"])) != len(payload["proposition_ids"]):
        raise PolicyError("Family members must be unique")
    for rid in payload["proposition_ids"]:
        ref("proposition", rid)


def validate_claim_card(ledger, payload, ref):
    ref("proposition", payload["proposition_id"])
    if len(set(payload["review_ids"])) != len(payload["review_ids"]):
        raise PolicyError("Card reviews must be unique")
    for rid in payload["review_ids"]:
        review = ref("review", rid)
        if review["status"] != "reviewed" or review["proposition_id"] != payload["proposition_id"]:
            raise PolicyError("Claim card requires reviewed findings for this exact proposition")
        if datetime.fromisoformat(payload["valid_until"]) <= datetime.fromisoformat(
            review["reviewed_at"]
        ):
            raise PolicyError("Card expiry must follow its review dates")
