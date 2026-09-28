"""Versioned handoffs. Record schema versions and handler versions are independent."""

from __future__ import annotations

from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class RuntimeModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Binding(RuntimeModel):
    kind: str = Field(min_length=1, max_length=100)
    id: str = Field(min_length=1, max_length=180)
    revision: int = Field(ge=1, strict=True)
    record_hash: str = Field(pattern=r"^[a-f0-9]{64}$")


class ArtifactInput(RuntimeModel):
    key: str = Field(pattern=r"^sha256/[a-f0-9]{2}/[a-f0-9]{64}$")
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    size: int = Field(ge=0, strict=True)


class JobRequest(RuntimeModel):
    contract_version: Literal[1] = 1
    handler: str = Field(pattern=r"^[a-z][a-z0-9_.]{1,99}$")
    handler_version: Literal[1] = 1
    run_id: str = Field(
        default_factory=lambda: "run-" + uuid4().hex, pattern=r"^[a-zA-Z0-9_.:-]{1,180}$"
    )
    capability: Literal["cpu", "gpu"] = "cpu"
    inputs: list[Binding] = Field(default_factory=list, max_length=10000)
    artifacts: dict[str, ArtifactInput] = Field(default_factory=dict, max_length=100)
    parameters: dict[str, Any] = Field(default_factory=dict)
    config_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    max_attempts: int = Field(default=3, ge=1, le=10)


class ImportTranscript(RuntimeModel):
    asset_id: str
    transcript_id: str
    format: Literal["vtt", "srt", "asr"]
    engine: str = "operator-import"
    expected_revision: int = Field(default=0, ge=0, strict=True)


class Localize(RuntimeModel):
    profile_id: str
    transcript_id: str
    config: dict[str, Any] = Field(default_factory=dict)


class Clip(RuntimeModel):
    asset_id: str
    start_ms: int = Field(ge=0, strict=True)
    end_ms: int = Field(gt=0, strict=True)
    padding_ms: int = Field(default=15000, ge=0, strict=True)


class JevDecision(RuntimeModel):
    request: dict[str, Any]


class Transcribe(RuntimeModel):
    asset_id: str
    transcript_id: str
    model_manifest_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    expected_revision: int = Field(default=0, ge=0, strict=True)
