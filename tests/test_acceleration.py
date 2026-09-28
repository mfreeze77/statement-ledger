import copy
import json
from datetime import UTC, datetime

import pytest

from statement_ledger.acceleration_demo import seed_acceleration
from statement_ledger.claim_library import card_status, exact_scope_gate, search_claims
from statement_ledger.demo import PERSON_ID
from statement_ledger.evaluation import calibration_report, estimate_cost, evaluate_windows
from statement_ledger.intervals import complement, duration, intersection, merge, pad
from statement_ledger.localization import combined_work, plan_localization, semantic_request
from statement_ledger.policy import PolicyError
from statement_ledger.profiles import build_profile, tokens


@pytest.fixture
def accelerated(ledger):
    ledger.fixture = seed_acceleration(ledger)
    return ledger


def payload(ledger, kind, rid):
    return copy.deepcopy(ledger.store.get(kind, rid)["payload"])


def test_profile_contains_all_phrase_categories(accelerated):
    p = payload(accelerated, "speaker_profile", "profile-demo")
    assert p["readiness"] == "research_ready"
    assert {f["category"] for f in p["features"]} == {"opening", "closing", "phrase"}
    assert p["calibration"] == "uncalibrated" and len(p["target_event_ids"]) == 3


def test_profile_rejects_forged_derived_features(accelerated):
    p = payload(accelerated, "speaker_profile", "profile-demo")
    p["id"] = "forged"
    p["features"][0]["weight"] = 500
    with pytest.raises(PolicyError, match="reproducibly"):
        accelerated.put("speaker_profile", p)


def test_duplicate_turns_do_not_train_twice(accelerated):
    p = payload(accelerated, "speaker_profile", "profile-demo")
    u = payload(accelerated, "utterance", p["example_ids"][0])
    u["id"] = "copied-turn"
    accelerated.put("utterance", u)
    r = build_profile(
        accelerated,
        PERSON_ID,
        p["example_ids"] + [u["id"]],
        p["background_ids"],
        profile_id="dedup",
    )
    assert r["payload"]["features"] == p["features"]
    assert len(r["payload"]["duplicate_example_ids"]) == 1


def test_reject_training_on_candidate_turn(accelerated):
    p = payload(accelerated, "speaker_profile", "profile-demo")
    u = payload(accelerated, "utterance", p["example_ids"][0])
    u["id"] = "candidate-turn"
    u["status"] = "candidate"
    accelerated.put("utterance", u)
    with pytest.raises(PolicyError, match="accepted"):
        build_profile(accelerated, PERSON_ID, [u["id"]], p["background_ids"])


def test_background_must_not_be_target(accelerated):
    p = payload(accelerated, "speaker_profile", "profile-demo")
    with pytest.raises(PolicyError):
        build_profile(accelerated, PERSON_ID, p["example_ids"], p["example_ids"])


def test_missing_learning_right_is_not_ignored(seeded):
    with pytest.raises(PolicyError, match="learn_profile"):
        build_profile(seeded, PERSON_ID, ["utterance-asset-original"], [])


def test_cold_start_selects_full_asset(accelerated):
    build_profile(accelerated, PERSON_ID, [], [], profile_id="cold")
    r = plan_localization(
        accelerated, "cold", "style-heldout-transcript", config={"mode": "assist"}
    )["payload"]
    assert r["selected_audio_ms"] == 600000 and "cold_start_profile" in r["fallback_reasons"]


def test_shadow_does_not_skip_audio(accelerated):
    r = accelerated.fixture["shadow"]["run"]["payload"]
    assert r["selected_audio_ms"] == r["duration_ms"] and r["audio_reduction_fraction"] == 0
    assert r["proposed_audio_ms"] < r["duration_ms"]


def test_assist_preserves_target_and_rejected_windows(accelerated):
    r = accelerated.fixture["assist"]["run"]["payload"]
    assert 0 < r["selected_audio_ms"] < 600000
    assert r["unprocessed_intervals"] and any(w["disposition"] == "audit" for w in r["windows"])
    assert r["coverage_recall"] is None and not r["identities_confirmed"]
    assert accelerated.fixture["evaluation"]["target_time_recall"] == 1


def test_no_identity_maps_created_by_localization(accelerated):
    assert not [
        x
        for x in accelerated.store.all("speaker_mapping")
        if x["payload"]["transcript_id"] == "style-heldout-transcript"
    ]


def test_deterministic_plan_and_cache_id(accelerated):
    a = plan_localization(
        accelerated, "profile-demo", "style-heldout-transcript", config={"mode": "assist"}
    )
    b = plan_localization(
        accelerated, "profile-demo", "style-heldout-transcript", config={"mode": "assist"}
    )
    assert a["id"] == b["id"] and a["hash"] == b["hash"]


def test_profile_revision_invalidates_plan(accelerated):
    p = payload(accelerated, "person", PERSON_ID)
    p["aliases"] = ["A new public alias"]
    accelerated.put("person", p, 1)
    assert accelerated.store.get("speaker_profile", "profile-demo")["stale"]
    with pytest.raises(PolicyError):
        plan_localization(accelerated, "profile-demo", "style-heldout-transcript")


def test_large_window_budget_fails_open(accelerated):
    r = plan_localization(
        accelerated,
        "profile-demo",
        "style-heldout-transcript",
        config={"mode": "assist", "max_windows": 1},
    )["payload"]
    assert r["selected_audio_ms"] == 600000 and "window_budget_exceeded" in r["fallback_reasons"]


def test_captions_gaps_not_assumed_silence(accelerated):
    t = payload(accelerated, "transcript", "style-heldout-transcript")
    t["id"] = "gap-transcript"
    t["segments"] = t["segments"][:12]
    accelerated.put("transcript", t)
    r = plan_localization(accelerated, "profile-demo", t["id"], config={"mode": "assist"})[
        "payload"
    ]
    assert r["caption_gaps"] == [{"start_ms": 120000, "end_ms": 600000}]
    assert duration(intersection(r["selected_intervals"], [(120000, 600000)])) == 480000


def test_no_matches_fails_open(accelerated):
    t = payload(accelerated, "transcript", "style-heldout-transcript")
    t["id"] = "no-match-transcript"
    for s in t["segments"]:
        s["text"] = "Unrelated plain words."
    accelerated.put("transcript", t)
    r = plan_localization(accelerated, "profile-demo", t["id"], config={"mode": "assist"})[
        "payload"
    ]
    assert r["selected_audio_ms"] == 600000 and "no_positive_candidates" in r["fallback_reasons"]


def test_combining_two_identical_plans_does_not_double_cost(accelerated):
    rid = accelerated.fixture["assist"]["run"]["id"]
    result = combined_work(accelerated, [rid, rid])
    assert (
        result["style-heldout-asset"]["selected_audio_ms"]
        == accelerated.fixture["assist"]["run"]["payload"]["selected_audio_ms"]
    )


def test_forged_localization_rejected(accelerated):
    p = payload(accelerated, "localization_run", accelerated.fixture["assist"]["run"]["id"])
    p["id"] = "bad-plan"
    p["selected_audio_ms"] = 0
    with pytest.raises(PolicyError):
        accelerated.put("localization_run", p)


def test_semantic_requests_are_bounded_and_explicit(accelerated):
    batches, issues = semantic_request(accelerated, "profile-demo", "style-heldout-transcript")
    assert not issues and len(batches) == 5
    assert len(batches[0]["questions"]) == 8
    assert "windows[0].text" in next(iter(batches[0]["questions"].values()))["instructions"]
    assert "party" not in json.dumps(batches[0]["state"])


def test_semantic_request_budget_not_silently_complete(accelerated):
    batches, issues = semantic_request(
        accelerated, "profile-demo", "style-heldout-transcript", max_calls=1
    )
    assert len(batches) == 1 and issues == ["semantic_call_budget_exceeded"]


def test_unicode_tokenization():
    assert tokens("Café naïve — l’idée!") == ["café", "naïve", "l'idée"]


@pytest.mark.parametrize(
    "intervals,expected",
    [([(0, 10), (5, 15)], [(0, 15)]), ([(0, 10), (10, 20)], [(0, 20)]), ([], [])],
)
def test_interval_union(intervals, expected):
    assert merge(intervals) == expected


@pytest.mark.parametrize("invalid", [[(1, 1)], [(2, 1)], [(-1, 3)], [(True, 5)], [(1.5, 5)]])
def test_invalid_intervals(invalid):
    with pytest.raises(ValueError):
        merge(invalid)


def test_interval_algebra():
    assert intersection([(0, 20), (30, 40)], [(10, 35)]) == [(10, 20), (30, 35)]
    assert complement([(10, 20)], 30) == [(0, 10), (20, 30)]
    assert pad([(10, 20)], 15, 30) == [(0, 30)]


def test_eval_rejects_event_leakage():
    with pytest.raises(ValueError, match="overlaps"):
        evaluate_windows([(0, 10)], [(0, 10)], 20, event_id="x", training_event_ids=["x"])


def test_empty_truth_is_not_perfect_recall():
    r = evaluate_windows([(0, 10)], [], 20, event_id="x")
    assert r["target_time_recall"] is None and not r["deployment_gate_passed"]


def test_partial_capture_metrics():
    r = evaluate_windows([(0, 10)], [(5, 15)], 20, event_id="x")
    assert r["target_time_recall"] == 0.5 and r["missed_target_audio_ms"] == 5


def test_calibration_does_not_promote():
    r = calibration_report(
        [
            {"event_id": "x", "signal": 0.9, "target_present": True},
            {"event_id": "y", "signal": 0.1, "target_present": False},
        ]
    )
    assert r["brier_score"] == pytest.approx(0.01) and not r["threshold_promoted"]


def test_calibration_leakage_rejected():
    with pytest.raises(ValueError):
        calibration_report(
            [{"event_id": "x", "signal": 0.9, "target_present": True}], training_event_ids=["x"]
        )


@pytest.mark.parametrize("value", [-1, float("nan"), float("inf"), True])
def test_bad_costs_rejected(value):
    with pytest.raises(ValueError):
        estimate_cost(duration_ms=60000, selected_audio_ms=10000, audio_cost_per_minute=value)


def test_cost_includes_screening_and_can_lose():
    r = estimate_cost(
        duration_ms=60000, selected_audio_ms=12000, audio_cost_per_minute=0.01, verification_cost=1
    )
    assert r["estimated_savings"] < 0 and r["lower_estimated_cost_route"] == "full_audio"


def test_claim_index_search_and_rebuild(accelerated):
    a = search_claims(accelerated, "Synthetic Lab samples")
    assert a["items"][0]["proposition"]["id"] == "proposition-1"
    assert not a["automatic_review_reuse"]
    assert accelerated.store.rebuild_claim_index()["indexed"] >= 1


def test_claim_index_updates_on_revision(accelerated):
    p = payload(accelerated, "proposition", "proposition-1")
    p["text"] = "Different searchable xenolith topic"
    accelerated.put("proposition", p, 1)
    assert search_claims(accelerated, "xenolith")["items"][0]["proposition"]["id"] == p["id"]
    status = card_status(accelerated, accelerated.store.get("claim_card", "card-sample-count"))
    assert "stale_or_expired_dependency" in status["blocked_reasons"]


def test_fts_query_syntax_cannot_escape(accelerated):
    r = search_claims(accelerated, '" OR * NOT (near:syntax)')
    assert not r["automatic_review_reuse"]


def test_reuse_requires_complete_scope(accelerated):
    s = payload(accelerated, "proposition", "proposition-1")["scope"]
    assert exact_scope_gate(s, s)["compatible_candidate"]
    s2 = {**s, "period": "2024"}
    assert not exact_scope_gate(s, s2)["compatible_candidate"]
    s2 = {**s, "polarity": None}
    assert not exact_scope_gate(s2, s2)["compatible_candidate"]


def test_claim_card_never_automatically_reuses_verdict(accelerated):
    status = card_status(accelerated, accelerated.store.get("claim_card", "card-sample-count"))
    assert status["evidence_reuse_candidate"] and not status["automatic_verdict_reuse"]


def test_card_freshness_expiry(accelerated):
    p = payload(accelerated, "claim_card", "card-sample-count")
    p["valid_until"] = "2026-09-27T00:00:01+00:00"
    # Relative to review fixture this is a valid expired envelope.
    accelerated.put("claim_card", p, 1)
    assert (
        "freshness_expired"
        in card_status(accelerated, accelerated.store.get("claim_card", p["id"]))["blocked_reasons"]
    )


def test_open_correction_blocks_card_until_resolved(accelerated):
    c = {
        "id": "correction-test",
        "target_kind": "proposition",
        "target_id": "proposition-1",
        "observation_id": "demo-evidence",
        "text": "Check this source interpretation",
        "status": "reported",
    }
    accelerated.put("correction", c)
    assert (
        "open_correction"
        in card_status(accelerated, accelerated.store.get("claim_card", "card-sample-count"))[
            "blocked_reasons"
        ]
    )
    c.update(
        status="resolved",
        reviewer="test-reviewer",
        resolution="Reviewed and retained with this rationale",
        resolved_at=datetime.now(UTC).isoformat(),
    )
    accelerated.put("correction", c, 1)
    assert not card_status(accelerated, accelerated.store.get("claim_card", "card-sample-count"))[
        "open_correction_ids"
    ]


def test_legacy_scope_not_auto_reusable(seeded):
    s = payload(seeded, "proposition", "proposition-1")["scope"]
    assert not exact_scope_gate(s, s)["compatible_candidate"]


def test_primary_context_does_not_justify_factual_finding(seeded):
    e = payload(seeded, "evidence", "evidence-1")
    e["id"] = "only-context"
    e["relation"] = "context"
    seeded.put("evidence", e)
    review = payload(seeded, "review", "review-1")
    review["id"] = "bad-review"
    review["evidence_ids"] = [e["id"]]
    with pytest.raises(PolicyError):
        seeded.put("review", review)


def test_incremental_profile_refresh_only_accepted(accelerated):
    from statement_ledger.profiles import refresh_profile

    before = payload(accelerated, "speaker_profile", "profile-demo")
    r = refresh_profile(accelerated, "profile-demo", holdout_event_ids=["style-heldout-event"])
    assert not r["automatically_confirmed_turns"]
    assert r["profile"]["revision"] >= 1
    assert "style-heldout-event" not in r["profile"]["payload"]["target_event_ids"]
    assert r["profile"]["payload"]["background_ids"] == before["background_ids"]


def test_bulk_claim_seeds_are_not_verdicts(accelerated, tmp_path):
    from statement_ledger.claim_seeds import import_claim_seeds

    path = tmp_path / "seeds.jsonl"
    row = {
        "native_id": "s1",
        "source_url": "https://example.org/s1",
        "claim_text": "A synthetic claim to investigate",
        "scope": {},
    }
    path.write_text(json.dumps(row) + "\n" + json.dumps(row) + "\n")
    before = accelerated.store.counts().get("review", 0)
    r = import_claim_seeds(
        accelerated, path, "manual_import", "demo-rights", archive_root=tmp_path / "raw"
    )
    assert r["success"] and r["created_propositions"] == 1 and r["unchanged_propositions"] == 1
    assert r["findings_created"] == 0 and accelerated.store.counts()["review"] == before
    found = search_claims(accelerated, "investigate")["items"][0]["proposition"]["payload"]
    assert found["kind"] == "ambiguous" and found["seed_observation_ids"]


def test_bulk_claim_seeds_reject_imported_truth_label(accelerated, tmp_path):
    from statement_ledger.claim_seeds import import_claim_seeds

    path = tmp_path / "bad.jsonl"
    path.write_text(
        json.dumps(
            {
                "native_id": "s1",
                "source_url": "https://example.org/s1",
                "claim_text": "Claim",
                "finding": "contradicted",
            }
        )
        + "\n"
    )
    r = import_claim_seeds(
        accelerated, path, "manual_import", "demo-rights", archive_root=tmp_path / "raw"
    )
    assert not r["success"] and r["errors"] and r["findings_created"] == 0


def test_adjacent_distinct_gold_turns_are_counted_separately():
    from statement_ledger.evaluation import evaluate_windows

    result = evaluate_windows([(0, 20)], [(0, 10), (10, 20)], 20, event_id="heldout")
    assert (
        result["target_audio_ms"] == 20
        and result["gold_turns"] == 2
        and result["fully_covered_turns"] == 2
    )


def test_cost_model_counts_output_tokens():
    from statement_ledger.evaluation import estimate_cost

    result = estimate_cost(
        duration_ms=60000,
        selected_audio_ms=30000,
        audio_cost_per_minute=1,
        screening_input_tokens=1000000,
        price_per_million_input_tokens=0.2,
        screening_output_tokens=1000000,
        price_per_million_output_tokens=0.4,
    )
    assert result["screening_cost"] == pytest.approx(0.6)
    assert result["estimated_savings"] == pytest.approx(-0.1)
