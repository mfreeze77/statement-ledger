from __future__ import annotations

from statement_ledger.contracts.models import RightsGrant
from statement_ledger.core.policy import PolicyError, require_right


def validate_transcript(ledger, payload, ref):
    asset = ref("asset", payload["asset_id"])
    grant = RightsGrant.model_validate(ref("rights", asset["rights_id"]))
    require_right(grant, "store_text")
    if payload["input_sha256"] and payload["input_sha256"] != asset["content_sha256"]:
        raise PolicyError("Transcript input hash does not match the registered source asset")
    last_start = -1
    for s in payload["segments"]:
        if s["end_ms"] > asset["duration_ms"]:
            raise PolicyError("Transcript segment exceeds asset duration")
        if s["start_ms"] < last_start:
            raise PolicyError("Segments must be sorted by start time; overlap remains allowed")
        last_start = s["start_ms"]


def validate_speaker_mapping(ledger, payload, ref):
    transcript = ref("transcript", payload["transcript_id"])
    ref("person", payload["person_id"])
    if payload["speaker_label"] not in {s["speaker_label"] for s in transcript["segments"]}:
        raise PolicyError("Speaker label is absent from this transcript")
    if payload["status"] == "confirmed":
        if payload["speaker_label"] in {"unassigned", "unknown"}:
            raise PolicyError(
                "Unassigned audio must be diarized or manually segmented before naming a person"
            )
        for row in ledger.store.all("speaker_mapping"):
            other = row["payload"]
            if (
                other["id"] != payload["id"]
                and (not row["stale"])
                and (other["status"] == "confirmed")
                and (other["transcript_id"] == payload["transcript_id"])
                and (other["speaker_label"] == payload["speaker_label"])
            ):
                raise PolicyError(
                    "This transcript label already has a confirmed mapping; revise that record"
                )


def validate_utterance(ledger, payload, ref):
    transcript = ref("transcript", payload["transcript_id"])
    mapping = ref("speaker_mapping", payload["mapping_id"])
    appearance = ref("appearance", payload["appearance_id"])
    asset = ref("asset", transcript["asset_id"])
    if mapping["transcript_id"] != payload["transcript_id"]:
        raise PolicyError("Speaker mapping belongs to another transcript")
    if (
        appearance["person_id"] != mapping["person_id"]
        or appearance["event_id"] != asset["event_id"]
    ):
        raise PolicyError("Appearance, person, and original event do not agree")
    indices = payload["segment_indices"]
    if indices != list(range(indices[0], indices[-1] + 1)):
        raise PolicyError("Utterance indices must be a nonduplicated contiguous range")
    if indices[-1] >= len(transcript["segments"]):
        raise PolicyError("Segment index out of bounds")
    segments = [transcript["segments"][i] for i in indices]
    if any(s["speaker_label"] != mapping["speaker_label"] for s in segments):
        raise PolicyError("Utterance contains words from another speaker")
    if payload["exact_text"] != " ".join(s["text"] for s in segments):
        raise PolicyError("Exact text must match retained transcript segments verbatim")
    if payload["status"] == "accepted":
        if (
            not payload["reviewer"]
            or not payload["context_reviewed"]
            or mapping["status"] != "confirmed"
            or (appearance["status"] != "confirmed")
        ):
            raise PolicyError(
                "Acceptance requires confirmed identity/appearance and context review"
            )
        if any(s["overlap"] for s in segments) and (not payload["overlap_resolved"]):
            raise PolicyError("Overlapping speech requires explicit resolution")


def validate_speaker_profile(ledger, payload, ref):
    from statement_ledger.pillars.speech.profiles import derive_profile

    ref("person", payload["person_id"])
    for uid in payload["example_ids"] + payload["background_ids"]:
        ref("utterance", uid)
    expected = derive_profile(
        ledger,
        payload["person_id"],
        payload["example_ids"],
        payload["background_ids"],
        payload["config"],
    )
    if {k: v for k, v in payload.items() if k != "id"} != expected:
        raise PolicyError("Profile must be reproducibly derived from accepted source turns")


def validate_localization_run(ledger, payload, ref):
    from statement_ledger.pillars.speech.localization import derive_localization

    ref("speaker_profile", payload["profile_id"])
    ref("transcript", payload["transcript_id"])
    ref("asset", payload["asset_id"])
    for rid in payload["decision_run_ids"]:
        ref("decision_run", rid)
    for b in payload["bindings"]:
        ref(b["kind"], b["id"])
        if ledger.store.get(b["kind"], b["id"])["revision"] != b["revision"]:
            raise PolicyError("Localization dependency changed")
    expected = derive_localization(
        ledger,
        payload["profile_id"],
        payload["transcript_id"],
        payload["config"],
        payload["decision_run_ids"],
    )
    if {k: v for k, v in payload.items() if k != "id"} != expected:
        raise PolicyError("Localization output must match its source/configuration")
