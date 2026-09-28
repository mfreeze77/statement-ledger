from __future__ import annotations

from statement_ledger.contracts.models import KINDS
from statement_ledger.core.policy import PolicyError


def validate_evidence(ledger, payload, ref):
    ref("proposition", payload["proposition_id"])
    obs = ref("observation", payload["observation_id"])
    text = obs.get("text")
    if not text or payload["excerpt"] not in text:
        raise PolicyError("Evidence excerpt must occur verbatim in the retained observation text")
    if payload["source_type"] == "primary" and obs["kind"] in {"external_review", "media_review"}:
        raise PolicyError("External reviews cannot be relabeled as primary evidence")


def validate_review(ledger, payload, ref):
    prop = ref("proposition", payload["proposition_id"])
    occurrences = [ref("occurrence", oid) for oid in payload["occurrence_ids"]]
    evidence = [ref("evidence", eid) for eid in payload["evidence_ids"]]
    if any(o["proposition_id"] != payload["proposition_id"] for o in occurrences):
        raise PolicyError("Review occurrences refer to another proposition")
    if any(e["proposition_id"] != payload["proposition_id"] for e in evidence):
        raise PolicyError("Review evidence belongs to another proposition")
    if payload["status"] == "reviewed":
        if not payload["reviewer"] or not payload["reviewed_at"] or (not payload["scope_reviewed"]):
            raise PolicyError("Completed review requires reviewer, date, and explicit scope review")
        if any(
            not o["extraction_reviewed_by"] or o["assertion"] != "asserted" for o in occurrences
        ):
            raise PolicyError("Completed factual review requires reviewed asserted occurrences")
        if payload["finding"] in {"supported", "contradicted", "mixed"}:
            if prop["kind"] != "empirical" or not evidence:
                raise PolicyError(
                    "A factual finding requires an empirical proposition and evidence"
                )
            for e in evidence:
                if e["relation"] in {"supports", "conflicts"}:
                    for field in (
                        "entity",
                        "metric",
                        "geography",
                        "period",
                        "unit",
                        "definition",
                        "baseline",
                        "comparator",
                        "polarity",
                        "conditions",
                        "population",
                        "accounting_basis",
                        "document_version",
                    ):
                        if e["applicable_scope"].get(field) != prop["scope"].get(field):
                            raise PolicyError(
                                "Evidence scope mismatch; do not reuse a different proposition"
                            )
                    if any(
                        not prop["scope"][key]
                        for key in ("entity", "metric", "geography", "period", "unit", "definition")
                    ):
                        raise PolicyError(
                            "Complete factual scope or mark explicitly not_applicable before review"
                        )
            if not any(
                e["source_type"] == "primary" and e["relation"] in {"supports", "conflicts"}
                for e in evidence
            ):
                raise PolicyError("A completed factual finding needs underlying primary evidence")
        if payload["finding"] == "contradicted" and (
            not any(
                e["relation"] == "conflicts" and e["source_type"] == "primary" for e in evidence
            )
        ):
            raise PolicyError("Contradicted finding requires conflicting evidence")
        if payload["finding"] == "supported" and (
            not any(e["relation"] == "supports" and e["source_type"] == "primary" for e in evidence)
        ):
            raise PolicyError("Supported finding requires supporting evidence")
        if payload["finding"] == "mixed" and (
            not {"supports", "conflicts"} <= {e["relation"] for e in evidence}
        ):
            raise PolicyError("Mixed finding requires supporting and conflicting evidence")


def validate_correction(ledger, payload, ref):
    if payload["target_kind"] not in KINDS:
        raise PolicyError("Unknown correction target kind")
    ref(payload["target_kind"], payload["target_id"])
    ref("observation", payload["observation_id"])
    if payload["status"] in {"verified", "resolved"} and (not payload["reviewer"]):
        raise PolicyError("Verified/resolved correction needs a reviewer")
    if payload["status"] == "resolved" and (
        not payload["resolution"] or not payload["resolved_at"]
    ):
        raise PolicyError("Resolved correction needs a dated resolution")
