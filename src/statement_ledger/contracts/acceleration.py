"""Versioned research artifacts. No artifact in this module confirms identity or truth."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any, Literal

from pydantic import Field, model_validator

from statement_ledger.contracts.models import ID, Millis, Model, Record, Text

Finite = Annotated[float, Field(allow_inf_nan=False)]
Probability = Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)]


class RecordRef(Model):
    kind: ID
    id: ID
    revision: Annotated[int, Field(ge=1, strict=True)]


class Interval(Model):
    start_ms: Millis
    end_ms: Millis

    @model_validator(mode="after")
    def ordered(self):
        if self.end_ms <= self.start_ms:
            raise ValueError("Interval must have positive duration")
        return self


class ProfileConfig(Model):
    min_events: Annotated[int, Field(ge=1, le=100)] = 2
    min_background_events: Annotated[int, Field(ge=1, le=100)] = 2
    min_feature_events: Annotated[int, Field(ge=1, le=100)] = 2
    max_features: Annotated[int, Field(ge=1, le=500)] = 100
    min_ngram: Annotated[int, Field(ge=1, le=5)] = 2
    max_ngram: Annotated[int, Field(ge=1, le=5)] = 4

    @model_validator(mode="after")
    def order(self):
        if self.min_ngram > self.max_ngram:
            raise ValueError("min_ngram exceeds max_ngram")
        return self


class PhraseFeature(Model):
    category: Literal["opening", "closing", "phrase"]
    phrase: Text
    target_events: Annotated[int, Field(ge=1)]
    background_events: Annotated[int, Field(ge=0)]
    weight: Annotated[float, Field(gt=0, allow_inf_nan=False)]


class SpeakerProfile(Record):
    person_id: ID
    example_ids: list[ID] = Field(default_factory=list, max_length=10000)
    background_ids: list[ID] = Field(default_factory=list, max_length=10000)
    config: ProfileConfig = Field(default_factory=ProfileConfig)
    algorithm: Literal["event-log-odds-v1"] = "event-log-odds-v1"
    features: list[PhraseFeature] = Field(default_factory=list, max_length=500)
    target_event_ids: list[ID] = Field(default_factory=list)
    background_event_ids: list[ID] = Field(default_factory=list)
    retained_example_ids: list[ID] = Field(default_factory=list)
    duplicate_example_ids: list[ID] = Field(default_factory=list)
    bindings: list[RecordRef] = Field(default_factory=list)
    readiness: Literal["cold_start", "research_ready"] = "cold_start"
    limitations: list[str] = Field(default_factory=list)
    calibration: Literal["uncalibrated"] = "uncalibrated"


class LocalizationConfig(Model):
    mode: Literal["shadow", "assist"] = "shadow"
    window_ms: Annotated[int, Field(ge=1000, le=180000, strict=True)] = 30000
    stride_ms: Annotated[int, Field(ge=1000, le=180000, strict=True)] = 15000
    padding_ms: Annotated[int, Field(ge=0, le=180000, strict=True)] = 10000
    lexical_threshold: Annotated[float, Field(ge=0, allow_inf_nan=False)] = 1.0
    semantic_threshold: Probability = 0.35
    audit_fraction: Probability = 0.1
    audit_seed: str = "audit-v1"
    max_windows: Annotated[int, Field(ge=1, le=5000, strict=True)] = 1000
    full_processing_fraction: Probability = 0.85

    @model_validator(mode="after")
    def no_holes(self):
        if self.stride_ms > self.window_ms:
            raise ValueError("stride_ms cannot exceed window_ms")
        return self


class CandidateWindow(Interval):
    id: ID
    segment_indices: list[int]
    lexical_score: Annotated[float, Field(ge=0, allow_inf_nan=False)]
    matched_features: list[str] = Field(default_factory=list)
    handoff_hint: bool = False
    semantic_signal: Probability | None = None
    disposition: Literal["candidate", "audit", "unprocessed", "fallback"]
    reasons: list[str] = Field(default_factory=list)


class LocalizationRun(Record):
    profile_id: ID
    transcript_id: ID
    asset_id: ID
    config: LocalizationConfig
    duration_ms: Millis
    windows: list[CandidateWindow] = Field(max_length=5000)
    proposed_intervals: list[Interval]
    selected_intervals: list[Interval]
    unprocessed_intervals: list[Interval]
    caption_gaps: list[Interval]
    decision_run_ids: list[ID] = Field(default_factory=list, max_length=1000)
    fallback_reasons: list[str] = Field(default_factory=list)
    bindings: list[RecordRef]
    proposed_audio_ms: Millis
    selected_audio_ms: Millis
    audio_reduction_fraction: Probability
    coverage_recall: None = None
    identities_confirmed: Literal[False] = False
    probability_calibrated: Literal[False] = False


class DecisionRun(Record):
    purpose: Literal["speaker_localization", "claim_matching"]
    request_hash: Annotated[str, Field(pattern=r"^[a-f0-9]{64}$")]
    model_requested: Text
    model_resolved: str | None = None
    question_version: Text
    questions: dict[str, Any]
    answers: dict[str, Any] = Field(default_factory=dict)
    bindings: list[RecordRef] = Field(min_length=1)
    input_ids: list[str] = Field(default_factory=list)
    state_sha256: Annotated[str, Field(pattern=r"^[a-f0-9]{64}$")]
    status: Literal["available", "unavailable"]
    error_code: str | None = None
    warnings: list[str] = Field(default_factory=list)
    receipt_ids: list[ID] = Field(default_factory=list)
    latency_ms: Annotated[float, Field(ge=0, allow_inf_nan=False)]
    usage: dict[str, int] = Field(default_factory=dict)
    captured_at: datetime

    @model_validator(mode="after")
    def fault_is_not_answer(self):
        if self.status == "unavailable" and (self.answers or not self.error_code):
            raise ValueError("Unavailable evaluation requires an error and no semantic answers")
        if self.status == "available" and (self.error_code or not self.answers):
            raise ValueError("Available evaluation requires validated answers")
        return self


class ClaimFamily(Record):
    title: Text
    description: str = ""
    proposition_ids: list[ID] = Field(min_length=1, max_length=10000)
    grouping_basis: Text
    reviewer: Text
    equivalence_asserted: Literal[False] = False


class ClaimCard(Record):
    proposition_id: ID
    review_ids: list[ID] = Field(min_length=1, max_length=1000)
    valid_until: datetime
    freshness_rationale: Text
    approved_by: Text
    automatic_verdict_reuse: Literal[False] = False


class CalibrationRow(Model):
    event_id: ID
    signal: Probability
    target_present: bool = Field(strict=True)


EXTENSION_KINDS = {
    "speaker_profile": SpeakerProfile,
    "localization_run": LocalizationRun,
    "decision_run": DecisionRun,
    "claim_family": ClaimFamily,
    "claim_card": ClaimCard,
}
