"""End-to-end synthetic profile/window/library fixture. Never attributes real speech."""

from __future__ import annotations

from statement_ledger.application.acceleration import localize
from statement_ledger.application.demo import PERSON_ID, seed
from statement_ledger.application.evaluation import evaluate_windows
from statement_ledger.core.util import digest
from statement_ledger.pillars.claims.library import search_claims
from statement_ledger.pillars.speech.profiles import build_profile

TARGET_TEXTS = [
    "Look at the underlying record, this question needs context. That is the distinction.",
    "Look at the underlying record, the comparison needs context. That is the distinction.",
    "Look at the underlying record, we should inspect the document. That is the distinction.",
]
BACKGROUND_TEXTS = [
    "Thanks for joining the discussion. We will move to the next item.",
    "Thanks for joining the discussion. We have another item on the agenda.",
    "Thanks for joining the discussion. The meeting continues after this item.",
]


def seed_acceleration(ledger):
    if ledger.store.counts():
        raise ValueError("Acceleration demo requires an empty database")
    seed(ledger, expanded=True)
    w = ledger.put
    w(
        "person",
        {
            "id": "synthetic-pat-example",
            "display_name": "Pat Example (synthetic)",
            "synthetic": True,
        },
    )

    def event(eid):
        raw = {"id": eid, "synthetic": True, "text": "A synthetic recording for offline tests."}
        oid = f"obs-{eid}"
        w(
            "observation",
            {
                "id": oid,
                "source_id": "manual_import",
                "native_id": oid,
                "rights_id": "demo-rights",
                "kind": "appearance_lead",
                "url": f"https://example.org/{oid}",
                "text": raw["text"],
                "raw_payload": raw,
                "raw_sha256": digest(raw),
            },
        )
        w(
            "event",
            {
                "id": eid,
                "title": "Synthetic language experiment",
                "observation_ids": [oid],
                "synthetic": True,
            },
        )
        return oid

    ids = [[], []]
    for group, (pid, texts) in enumerate(
        ((PERSON_ID, TARGET_TEXTS), ("synthetic-pat-example", BACKGROUND_TEXTS))
    ):
        for i, text in enumerate(texts):
            eid = f"style-event-{group}-{i}"
            oid = event(eid)
            aid = f"asset-{eid}"
            tid = f"transcript-{eid}"
            mid = f"mapping-{eid}"
            uid = f"utterance-{eid}"
            w(
                "asset",
                {
                    "id": aid,
                    "event_id": eid,
                    "observation_id": oid,
                    "rights_id": "demo-rights",
                    "url": f"https://example.org/{aid}",
                    "duration_ms": 30000,
                },
            )
            w(
                "appearance",
                {
                    "id": f"appearance-{eid}",
                    "event_id": eid,
                    "person_id": pid,
                    "observation_ids": [oid],
                    "status": "confirmed",
                    "reviewer": "synthetic-fixture",
                    "rationale": "Fictional known turn",
                },
            )
            w(
                "transcript",
                {
                    "id": tid,
                    "asset_id": aid,
                    "engine": "synthetic-fixture",
                    "segments": [
                        {"start_ms": 0, "end_ms": 15000, "speaker_label": "speaker_0", "text": text}
                    ],
                },
            )
            w(
                "speaker_mapping",
                {
                    "id": mid,
                    "transcript_id": tid,
                    "speaker_label": "speaker_0",
                    "person_id": pid,
                    "status": "confirmed",
                    "evidence": ["Synthetic known turn"],
                    "reviewer": "synthetic-fixture",
                },
            )
            w(
                "utterance",
                {
                    "id": uid,
                    "transcript_id": tid,
                    "mapping_id": mid,
                    "appearance_id": f"appearance-{eid}",
                    "segment_indices": [0],
                    "exact_text": text,
                    "status": "accepted",
                    "context_reviewed": True,
                    "reviewer": "synthetic-fixture",
                },
            )
            ids[group].append(uid)
    profile = build_profile(ledger, PERSON_ID, *ids, profile_id="profile-demo")
    eid = "style-heldout-event"
    oid = event(eid)
    w(
        "asset",
        {
            "id": "style-heldout-asset",
            "event_id": eid,
            "observation_id": oid,
            "rights_id": "demo-rights",
            "url": "https://example.org/heldout",
            "duration_ms": 600000,
        },
    )
    segments = []
    for start in range(0, 600000, 10000):
        text = (
            TARGET_TEXTS[0]
            if start in {100000, 400000}
            else "The discussion continues with ordinary unrelated meeting material."
        )
        segments.append(
            {
                "start_ms": start,
                "end_ms": start + 10000,
                "speaker_label": "unassigned",
                "text": text,
            }
        )
    w(
        "transcript",
        {
            "id": "style-heldout-transcript",
            "asset_id": "style-heldout-asset",
            "engine": "synthetic-captions",
            "segments": segments,
        },
    )
    assist = localize(ledger, "profile-demo", "style-heldout-transcript", config={"mode": "assist"})
    shadow = localize(ledger, "profile-demo", "style-heldout-transcript", config={"mode": "shadow"})
    w(
        "claim_family",
        {
            "id": "family-sample-count",
            "title": "Synthetic Lab sample count",
            "description": "Related counts can disagree; this is not an equivalence class.",
            "proposition_ids": ["proposition-1"],
            "grouping_basis": "Synthetic metric topic",
            "reviewer": "synthetic-fixture",
        },
    )
    w(
        "claim_card",
        {
            "id": "card-sample-count",
            "proposition_id": "proposition-1",
            "review_ids": ["review-1"],
            "valid_until": "2027-01-01T00:00:00+00:00",
            "freshness_rationale": "Synthetic static fixture, not a real evidence policy",
            "approved_by": "synthetic-fixture",
        },
    )
    run = assist["run"]["payload"]
    labels = [{"start_ms": 100000, "end_ms": 110000}, {"start_ms": 400000, "end_ms": 410000}]
    evaluation = evaluate_windows(
        run["selected_intervals"],
        labels,
        600000,
        event_id=eid,
        training_event_ids=profile["payload"]["target_event_ids"]
        + profile["payload"]["background_event_ids"],
        truth_complete=True,
    )
    return {
        "synthetic": True,
        "profile_id": "profile-demo",
        "profile_input": {"person_id": PERSON_ID, "example_ids": ids[0], "background_ids": ids[1]},
        "assist": assist,
        "shadow": shadow,
        "evaluation": evaluation,
        "claim_search": search_claims(ledger, "Synthetic Lab processed samples"),
        "limitations": [
            "No Jev network call or speech-model inference executed.",
            "Synthetic coverage is not a real-world accuracy benchmark.",
        ],
    }
