from __future__ import annotations

from datetime import UTC, date, datetime
from typing import Annotated, Any, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

ID = Annotated[str, StringConstraints(min_length=1, max_length=180, pattern=r"^[a-zA-Z0-9_.:-]+$")]
Text = Annotated[str, StringConstraints(min_length=1, max_length=100_000)]
Millis = Annotated[int, Field(strict=True, ge=0)]


def now() -> datetime:
    return datetime.now(UTC)


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    @model_validator(mode="after")
    def aware_dates(self):
        for key in type(self).model_fields:
            value = getattr(self, key)
            if isinstance(value, datetime) and value.tzinfo is None:
                raise ValueError(f"{key} requires an explicit timezone")
        return self


class Record(Model):
    id: ID = Field(default_factory=lambda: str(uuid4()))


class Person(Record):
    display_name: Annotated[str, StringConstraints(min_length=1, max_length=250)]
    aliases: list[str] = Field(default_factory=list, max_length=50)
    identity_urls: list[str] = Field(default_factory=list, max_length=30)
    synthetic: bool = False


class RightsGrant(Record):
    source_id: ID
    basis: Text
    allowed: list[
        Literal[
            "discover",
            "store_text",
            "store_media",
            "process_audio",
            "derive_clip",
            "publish_excerpt",
            "publish_media",
            "send_to_provider",
            "index_external",
            "learn_profile",
            "process_biometrics",
        ]
    ] = Field(default_factory=list)
    evidence_url: str | None = None
    expires_at: datetime | None = None
    reviewed_by: str

    @model_validator(mode="after")
    def check(self):
        if not self.reviewed_by.strip():
            raise ValueError("Rights reviewer is required")
        if self.expires_at and self.expires_at.tzinfo is None:
            raise ValueError("expires_at must have an explicit timezone")
        return self


class Observation(Record):
    source_id: ID
    native_id: Text
    rights_id: ID
    kind: Literal[
        "appearance_lead",
        "quotation_lead",
        "external_review",
        "media_review",
        "transcript_lead",
        "frequency_signal",
        "metadata",
        "primary_document",
    ]
    url: str
    title: str = ""
    text: str | None = None
    reported_speaker: str | None = None
    published_at: str | None = (
        None  # Uncertain/partial publisher dates are preserved, not invented.
    )
    links: list[str] = Field(default_factory=list, max_length=10_000)
    raw_payload: dict[str, Any]
    retrieved_at: datetime = Field(default_factory=now)
    raw_sha256: Annotated[str, StringConstraints(pattern=r"^[a-f0-9]{64}$")]
    parser_version: str = "1"


class Event(Record):
    title: Text
    occurred_at: str | None = None
    date_precision: Literal["unknown", "year", "month", "day", "instant"] = "unknown"
    observation_ids: list[ID] = Field(min_length=1)
    date_evidence: str | None = None
    synthetic: bool = False

    @model_validator(mode="after")
    def date_proof(self):
        if not self.occurred_at and self.date_precision != "unknown":
            raise ValueError("Unknown date must have unknown precision")
        if self.occurred_at and (self.date_precision == "unknown" or not self.date_evidence):
            raise ValueError(
                "An event date requires precision and evidence; upload time is not event time"
            )
        return self


class Appearance(Record):
    event_id: ID
    person_id: ID
    observation_ids: list[ID] = Field(min_length=1)
    status: Literal["candidate", "confirmed", "mentioned_only", "rejected"] = "candidate"
    reviewer: str | None = None
    rationale: str | None = None

    @model_validator(mode="after")
    def confirmation(self):
        if self.status == "confirmed" and (not self.reviewer or not self.rationale):
            raise ValueError("A confirmed appearance needs a reviewer and evidence rationale")
        return self


class Asset(Record):
    event_id: ID
    observation_id: ID
    rights_id: ID
    url: str
    role: Literal["original", "copy", "excerpt", "unknown"] = "unknown"
    duration_ms: Millis
    content_sha256: Annotated[str, StringConstraints(pattern=r"^[a-f0-9]{64}$")] | None = None
    event_offset_ms: Annotated[int, Field(strict=True)] | None = None
    alignment_reviewed_by: str | None = None
    alignment_evidence: str | None = None
    published_at: str | None = None

    @model_validator(mode="after")
    def alignment(self):
        if self.event_offset_ms is not None and (
            not self.alignment_reviewed_by or not self.alignment_evidence
        ):
            raise ValueError("Event alignment requires human-reviewed evidence")
        return self


class Segment(Model):
    start_ms: Millis
    end_ms: Millis
    speaker_label: ID
    text: Text
    overlap: bool = False

    @model_validator(mode="after")
    def interval(self):
        if self.end_ms <= self.start_ms:
            raise ValueError("end_ms must be greater than start_ms")
        return self


class Transcript(Record):
    asset_id: ID
    engine: Text
    language: str = "en"
    segments: list[Segment] = Field(min_length=1, max_length=100_000)
    model_revision: str | None = None
    input_sha256: Annotated[str, StringConstraints(pattern=r"^[a-f0-9]{64}$")] | None = None
    precision: Literal["segment", "word", "manual"] = "segment"


class SpeakerMapping(Record):
    transcript_id: ID
    speaker_label: ID
    person_id: ID
    status: Literal["candidate", "confirmed", "rejected"] = "candidate"
    evidence: list[str] = Field(default_factory=list)
    reviewer: str | None = None

    @model_validator(mode="after")
    def identity(self):
        if self.status == "confirmed" and (not self.reviewer or not self.evidence):
            raise ValueError("Named speaker confirmation requires evidence and reviewer")
        return self


class Utterance(Record):
    transcript_id: ID
    mapping_id: ID
    appearance_id: ID
    segment_indices: list[Annotated[int, Field(strict=True, ge=0)]] = Field(min_length=1)
    exact_text: Text
    status: Literal["candidate", "accepted"] = "candidate"
    context_reviewed: bool = False
    overlap_resolved: bool = False
    reviewer: str | None = None


class Scope(Model):
    entity: str | None = None
    metric: str | None = None
    geography: str | None = None
    period: str | None = None
    unit: str | None = None
    baseline: str | None = None
    comparator: str | None = None
    quantity: str | None = None
    definition: str | None = None
    polarity: str | None = None
    conditions: str | None = None
    population: str | None = None
    accounting_basis: str | None = None
    document_version: str | None = None


class Proposition(Record):
    seed_observation_ids: list[ID] = Field(default_factory=list, max_length=10000)
    text: Text
    kind: Literal["empirical", "prediction", "opinion", "ambiguous"] = "empirical"
    scope: Scope


class Occurrence(Record):
    utterance_id: ID
    proposition_id: ID
    assertion: Literal["asserted", "quoted", "rejected", "hypothetical", "question", "unclear"]
    extraction_reviewed_by: str | None = None
    extraction_rationale: str | None = None


class Evidence(Record):
    observation_id: ID
    title: Text
    excerpt: Text
    locator: Text
    proposition_id: ID
    relation: Literal["supports", "conflicts", "context", "undetermined"] = "undetermined"
    source_type: Literal["primary", "secondary", "external_review"] = "primary"
    applicable_scope: Scope
    observed_at: datetime = Field(default_factory=now)


class Review(Record):
    proposition_id: ID
    occurrence_ids: list[ID] = Field(min_length=1)
    evidence_ids: list[ID] = Field(default_factory=list)
    status: Literal["draft", "reviewed"] = "draft"
    finding: Literal["supported", "contradicted", "mixed", "unresolved", "not_checkable"] = (
        "unresolved"
    )
    rationale: Text
    reviewer: str | None = None
    reviewed_at: datetime | None = None
    scope_reviewed: bool = False
    limitations: list[str] = Field(default_factory=list)


class Correction(Record):
    target_kind: str
    target_id: ID
    observation_id: ID
    text: Text
    status: Literal["reported", "verified", "resolved"] = "reported"
    resolution: str | None = None
    resolved_at: datetime | None = None
    reviewer: str | None = None


class CoverageRun(Record):
    person_id: ID
    source_id: ID
    query: str
    period_start: date
    period_end: date
    retrieved: Annotated[int, Field(ge=0)] = 0
    processed: Annotated[int, Field(ge=0)] = 0
    state: Literal["planned", "partial", "finished_query", "blocked", "failed"] = "planned"
    next_cursor: str | None = None
    limitation: Text


KINDS: dict[str, type[Record]] = {
    "person": Person,
    "rights": RightsGrant,
    "observation": Observation,
    "event": Event,
    "appearance": Appearance,
    "asset": Asset,
    "transcript": Transcript,
    "speaker_mapping": SpeakerMapping,
    "utterance": Utterance,
    "proposition": Proposition,
    "occurrence": Occurrence,
    "evidence": Evidence,
    "review": Review,
    "correction": Correction,
    "coverage_run": CoverageRun,
}
