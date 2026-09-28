import copy
from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from statement_ledger.demo import PERSON_ID, SCOPE
from statement_ledger.models import Event, RightsGrant, Segment
from statement_ledger.policy import PolicyError, require_right, scope_match
from statement_ledger.store import Conflict, Missing


def payload(ledger, kind, rid):
    return copy.deepcopy(ledger.store.get(kind, rid)["payload"])


def test_demo_deduplication(seeded):
    report = seeded.person_ledger(PERSON_ID)
    assert report["counts"] == {
        "eligible_recorded_assertion_rows": 3,
        "distinct_aligned_assertion_occurrences": 2,
        "distinct_propositions": 1,
        "excluded_rows": 0,
    }
    assert report["person_rating"] is None


def test_integrity(seeded):
    assert seeded.store.verify_audit()["valid"]
    assert seeded.store.verify_records()["valid"]


def test_expected_revision_required(seeded):
    p = payload(seeded, "person", PERSON_ID)
    with pytest.raises(Conflict):
        seeded.put("person", p, 0)
    assert seeded.put("person", p, 1)["revision"] == 1


def test_same_id_different_content_creates_revision(seeded):
    p = payload(seeded, "person", PERSON_ID)
    p["display_name"] = "Dana Example — revised synthetic name"
    result = seeded.put("person", p, 1)
    assert result["revision"] == 2
    assert len(seeded.store.history("person", PERSON_ID)) == 2


def test_person_revision_invalidates_descendants(seeded):
    p = payload(seeded, "person", PERSON_ID)
    p["aliases"] = ["D. Example"]
    seeded.put("person", p, 1)
    assert seeded.store.get("utterance", "utterance-asset-original")["stale"]
    assert seeded.store.get("review", "review-1")["stale"]
    assert seeded.person_ledger(PERSON_ID)["counts"]["distinct_aligned_assertion_occurrences"] == 0


def test_stale_dependency_blocks_new_review(seeded):
    p = payload(seeded, "proposition", "proposition-1")
    p["text"] += " Revised."
    seeded.put("proposition", p, 1)
    review = payload(seeded, "review", "review-1")
    review["id"] = "another-review"
    with pytest.raises(PolicyError):
        seeded.put("review", review)


def test_bad_checksum_rejected(seeded):
    p = payload(seeded, "observation", "demo-show")
    p["id"] = "wrong"
    p["raw_sha256"] = "0" * 64
    with pytest.raises(PolicyError, match="checksum"):
        seeded.put("observation", p)


def test_missing_reference_rejected(ledger):
    with pytest.raises(Missing):
        ledger.put("event", {"title": "x", "observation_ids": ["missing"]})


def test_no_invented_event_date():
    with pytest.raises(ValidationError):
        Event(title="x", observation_ids=["a"], occurred_at="2025-01-01")
    with pytest.raises(ValidationError):
        Event(title="x", observation_ids=["a"], date_precision="day")


@pytest.mark.parametrize("start,end", [(0, 0), (5, 4), (-1, 5), (1.5, 3)])
def test_invalid_interval(start, end):
    with pytest.raises(ValidationError):
        Segment(start_ms=start, end_ms=end, speaker_label="s", text="x")


def test_named_speaker_requires_evidence(seeded):
    p = payload(seeded, "speaker_mapping", "mapping-asset-original")
    p["id"] = "bad-mapping"
    p["evidence"] = []
    with pytest.raises(ValidationError):
        seeded.put("speaker_mapping", p)


def test_label_scope_transcript_not_global(seeded):
    p = payload(seeded, "utterance", "utterance-asset-original")
    p["id"] = "wrong-utterance"
    p["mapping_id"] = "mapping-asset-copy"
    with pytest.raises(PolicyError, match="another transcript"):
        seeded.put("utterance", p)


def test_cannot_invent_exact_text(seeded):
    p = payload(seeded, "utterance", "utterance-asset-original")
    p["id"] = "wrong-words"
    p["exact_text"] = "A fabricated quote"
    with pytest.raises(PolicyError, match="verbatim"):
        seeded.put("utterance", p)


def test_no_unreviewed_context_acceptance(seeded):
    p = payload(seeded, "utterance", "utterance-asset-original")
    p["id"] = "wrong-context"
    p["context_reviewed"] = False
    with pytest.raises(PolicyError):
        seeded.put("utterance", p)


def test_external_review_not_primary(seeded):
    obs = payload(seeded, "observation", "demo-evidence")
    obs["id"] = "external-source"
    obs["kind"] = "external_review"
    seeded.put("observation", obs)
    e = payload(seeded, "evidence", "evidence-1")
    e["id"] = "fake-primary"
    e["observation_id"] = "external-source"
    with pytest.raises(PolicyError, match="primary"):
        seeded.put("evidence", e)


def test_evidence_must_quote_retained_text(seeded):
    e = payload(seeded, "evidence", "evidence-1")
    e["id"] = "wrong-evidence"
    e["excerpt"] = "Unsupported excerpt"
    with pytest.raises(PolicyError, match="verbatim"):
        seeded.put("evidence", e)


def test_evidence_bound_to_proposition(seeded):
    prop = payload(seeded, "proposition", "proposition-1")
    prop["id"] = "proposition-2"
    seeded.put("proposition", prop)
    e = payload(seeded, "evidence", "evidence-1")
    e["id"] = "evidence-2"
    e["proposition_id"] = "proposition-2"
    seeded.put("evidence", e)
    review = payload(seeded, "review", "review-1")
    review["id"] = "bad-review"
    review["evidence_ids"] = ["evidence-2"]
    with pytest.raises(PolicyError, match="another proposition"):
        seeded.put("review", review)


def test_scope_mismatch_rejected(seeded):
    e = payload(seeded, "evidence", "evidence-1")
    e["id"] = "wrong-year"
    e["applicable_scope"]["period"] = "2024"
    seeded.put("evidence", e)
    review = payload(seeded, "review", "review-1")
    review["id"] = "bad-year-review"
    review["evidence_ids"] = ["wrong-year"]
    with pytest.raises(PolicyError, match="scope mismatch"):
        seeded.put("review", review)


@pytest.mark.parametrize(
    "field,value",
    [("reviewer", None), ("reviewed_at", None), ("scope_reviewed", False), ("evidence_ids", [])],
)
def test_review_gate(seeded, field, value):
    review = payload(seeded, "review", "review-1")
    review["id"] = "bad-review"
    review[field] = value
    with pytest.raises(PolicyError):
        seeded.put("review", review)


def test_opinion_not_empirical_finding(seeded):
    p = payload(seeded, "proposition", "proposition-1")
    p["id"] = "opinion"
    p["kind"] = "opinion"
    seeded.put("proposition", p)
    c = payload(seeded, "occurrence", "occurrence-asset-original")
    c["id"] = "opinion-occ"
    c["proposition_id"] = "opinion"
    seeded.put("occurrence", c)
    e = payload(seeded, "evidence", "evidence-1")
    e["id"] = "opinion-e"
    e["proposition_id"] = "opinion"
    seeded.put("evidence", e)
    r = payload(seeded, "review", "review-1")
    r.update(
        id="opinion-r",
        proposition_id="opinion",
        occurrence_ids=["opinion-occ"],
        evidence_ids=["opinion-e"],
    )
    with pytest.raises(PolicyError, match="empirical"):
        seeded.put("review", r)


@pytest.mark.parametrize("mode", ["quoted", "rejected", "hypothetical", "question", "unclear"])
def test_non_assertions_excluded(seeded, mode):
    c = payload(seeded, "occurrence", "occurrence-asset-original")
    c["assertion"] = mode
    seeded.put("occurrence", c, 1)
    r = seeded.person_ledger(PERSON_ID)
    assert any(x["reason"] == "not_an_assertion" for x in r["exclusions"])


def test_rights_expiry_removes_eligibility(seeded):
    p = payload(seeded, "rights", "demo-rights")
    p["expires_at"] = (datetime.now(UTC) - timedelta(seconds=1)).isoformat()
    seeded.put("rights", p, 1)
    assert seeded.person_ledger(PERSON_ID)["counts"]["distinct_aligned_assertion_occurrences"] == 0


def test_rights_operations_fail_closed():
    g = RightsGrant(
        id="r", source_id="youtube", basis="metadata", allowed=["discover"], reviewed_by="x"
    )
    with pytest.raises(PolicyError):
        require_right(g, "derive_clip")
    with pytest.raises(PolicyError):
        require_right(g, "discover", "aapb")


def test_datetimes_require_timezone():
    with pytest.raises(ValidationError):
        RightsGrant(
            source_id="manual_import", basis="x", reviewed_by="x", expires_at=datetime(2027, 1, 1)
        )


def test_scope_candidate_never_reuses_reviews():
    from statement_ledger.models import Scope

    assert scope_match(Scope(**SCOPE), Scope(**SCOPE))["compatible_candidate"]
    assert not scope_match(Scope(**SCOPE), Scope(**SCOPE))["automatic_review_reuse"]
    assert not scope_match(Scope(), Scope())["compatible_candidate"]


def test_cycle_rejected(seeded):
    # Make an observation depend on rights which already depends indirectly on it?
    # The graph traversal itself must detect back edges before any future schema extension.
    assert seeded.store.would_cycle(("person", PERSON_ID), ("review", "review-1"))


def test_audit_tamper_detected(seeded):
    seeded.store.db.execute("UPDATE audit SET event='{}' WHERE sequence=1")
    assert not seeded.store.verify_audit()["valid"]


def test_record_tamper_detected(seeded):
    seeded.store.db.execute("UPDATE revisions SET hash=? WHERE kind='person'", ("0" * 64,))
    assert not seeded.store.verify_records()["valid"]


def test_schema_forbids_unknown_fields(ledger):
    with pytest.raises(ValidationError):
        ledger.put("person", {"display_name": "Example", "lie_score": 3})


def test_failed_write_rolls_back(ledger):
    before = ledger.store.verify_audit()["checked"]
    with pytest.raises(Missing):
        ledger.put(
            "asset",
            {
                "event_id": "bad",
                "observation_id": "bad",
                "rights_id": "bad",
                "url": "https://example.org/",
                "duration_ms": 1,
            },
        )
    assert ledger.store.verify_audit()["checked"] == before
    assert ledger.store.counts() == {}
