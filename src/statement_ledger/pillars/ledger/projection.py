from __future__ import annotations

from statement_ledger.contracts.models import RightsGrant
from statement_ledger.core.errors import Missing
from statement_ledger.core.policy import PolicyError, require_right
from statement_ledger.core.util import digest


def person_ledger(ledger, person_id: str) -> dict:
    person = ledger.store.get("person", person_id)
    items, exclusions = ([], [])
    relevant_keys = {("person", person_id)}

    def collect(kind, rid):
        todo = [(kind, rid)]
        while todo:
            key = todo.pop()
            if key in relevant_keys:
                continue
            relevant_keys.add(key)
            record = ledger.store.get(*key)
            todo.extend((d["kind"], d["id"]) for d in record["dependencies"])

    for row in ledger.store.all("occurrence"):
        payload = row["payload"]
        try:
            u = ledger.store.get("utterance", payload["utterance_id"])
            m = ledger.store.get("speaker_mapping", u["payload"]["mapping_id"])
            if m["payload"]["person_id"] != person_id:
                continue
            collect("occurrence", payload["id"])
            t = ledger.store.get("transcript", u["payload"]["transcript_id"])
            a = ledger.store.get("asset", t["payload"]["asset_id"])
            ledger.store.get("appearance", u["payload"]["appearance_id"])
            ledger.store.get("proposition", payload["proposition_id"])
            reason = None
            if not ledger.dependencies_current("occurrence", payload["id"]):
                reason = "stale_dependency"
            elif u["payload"]["status"] != "accepted" or not payload["extraction_reviewed_by"]:
                reason = "review_incomplete"
            elif payload["assertion"] != "asserted":
                reason = "not_an_assertion"
            elif a["payload"]["event_offset_ms"] is None:
                reason = "unresolved_event_alignment"
            else:
                rights = ledger.store.get("rights", a["payload"]["rights_id"])
                try:
                    require_right(RightsGrant.model_validate(rights["payload"]), "store_text")
                except PolicyError:
                    reason = "rights_not_current"
            if reason:
                exclusions.append({"occurrence_id": payload["id"], "reason": reason})
                continue
            indices = u["payload"]["segment_indices"]
            segments = [t["payload"]["segments"][i] for i in indices]
            start = segments[0]["start_ms"] + a["payload"]["event_offset_ms"]
            end = segments[-1]["end_ms"] + a["payload"]["event_offset_ms"]
            if start < 0:
                exclusions.append(
                    {"occurrence_id": payload["id"], "reason": "invalid_event_alignment"}
                )
                continue
            key = digest(
                [a["payload"]["event_id"], person_id, payload["proposition_id"], start, end]
            )
            reviews = [
                r
                for r in ledger.store.all("review")
                if payload["id"] in r["payload"]["occurrence_ids"]
                and r["payload"]["status"] == "reviewed"
                and ledger.dependencies_current("review", r["id"])
            ]
            for reviewed in reviews:
                collect("review", reviewed["id"])
            items.append(
                {
                    "occurrence_id": payload["id"],
                    "canonical_key": key,
                    "event_id": a["payload"]["event_id"],
                    "asset_id": a["id"],
                    "asset_role": a["payload"]["role"],
                    "proposition_id": payload["proposition_id"],
                    "exact_text": u["payload"]["exact_text"],
                    "event_start_ms": start,
                    "event_end_ms": end,
                    "source_start_ms": segments[0]["start_ms"],
                    "source_end_ms": segments[-1]["end_ms"],
                    "source_url": a["payload"]["url"],
                    "reviews": reviews,
                }
            )
        except Missing:
            exclusions.append({"occurrence_id": payload["id"], "reason": "missing_dependency"})
    appearances = [
        a for a in ledger.store.all("appearance") if a["payload"]["person_id"] == person_id
    ]
    coverage = [
        c for c in ledger.store.all("coverage_run") if c["payload"]["person_id"] == person_id
    ]
    return {
        "person": person,
        "items": items,
        "exclusions": exclusions,
        "appearances": appearances,
        "coverage": coverage,
        "counts": {
            "eligible_recorded_assertion_rows": len(items),
            "distinct_aligned_assertion_occurrences": len({i["canonical_key"] for i in items}),
            "distinct_propositions": len({i["proposition_id"] for i in items}),
            "excluded_rows": len(exclusions),
        },
        "coverage_statement": "Identified records only; not all appearances or all statements.",
        "deduplication_limit": "Exact human-reviewed event coordinates only; fuzzy offset reconciliation is not implemented.",
        "corrections": [
            c
            for c in ledger.store.all("correction")
            if (c["payload"]["target_kind"], c["payload"]["target_id"]) in relevant_keys
        ],
        "person_rating": None,
    }
