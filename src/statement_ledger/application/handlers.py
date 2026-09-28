"""Existing work wired through typed jobs; no autonomous discovery or review approval."""

from __future__ import annotations

import json
import uuid
from typing import Any, cast

from statement_ledger.contracts.models import RightsGrant, now
from statement_ledger.contracts.runtime import (
    Clip,
    ImportTranscript,
    JevDecision,
    JobRequest,
    Localize,
    Transcribe,
)
from statement_ledger.core.policy import require_right
from statement_ledger.core.util import canonical_json, digest
from statement_ledger.infrastructure.artifacts import Artifact
from statement_ledger.infrastructure.operations import OperationBlocked
from statement_ledger.infrastructure.queue import LeaseLost
from statement_ledger.infrastructure.secrets import LocalSecrets
from statement_ledger.infrastructure.worker import Handler, PreparedResult, RecordWrite, WorkContext
from statement_ledger.pillars.media.clipping import clip_plan, local_clip
from statement_ledger.pillars.speech.localization import derive_localization
from statement_ledger.pillars.speech.transcripts import from_asr_export, parse_timed_text


def bound(ledger: Any, job: JobRequest, kind: str, record_id: str) -> dict[str, Any]:
    matches = [binding for binding in job.inputs if (binding.kind, binding.id) == (kind, record_id)]
    if len(matches) != 1:
        raise ValueError("Required versioned input was not supplied")
    row = ledger.store.get(kind, record_id)
    if (
        row["revision"] != matches[0].revision
        or row["hash"] != matches[0].record_hash
        or not ledger.dependencies_current(kind, record_id)
    ):
        raise ValueError("Required input is not current")
    return cast(dict[str, Any], row["payload"])


def media_rights(
    ledger: Any, job: JobRequest, asset_id: str, operations: tuple[str, ...]
) -> dict[str, Any]:
    asset = bound(ledger, job, "asset", asset_id)
    grant = RightsGrant.model_validate(ledger.store.get("rights", asset["rights_id"])["payload"])
    for operation in operations:
        require_right(grant, operation)
    return asset


def validate_import(ledger: Any, job: JobRequest) -> None:
    params = ImportTranscript.model_validate(job.parameters)
    media_rights(ledger, job, params.asset_id, ("store_text",))
    if set(job.artifacts) != {"transcript"}:
        raise ValueError("Transcript import requires exactly one transcript artifact")


def prepare_import(context: WorkContext, job: JobRequest) -> PreparedResult:
    params = ImportTranscript.model_validate(job.parameters)
    artifact = Artifact(**job.artifacts["transcript"].model_dump())
    if artifact.size > 64 * 1024 * 1024:
        raise ValueError("Transcript exceeds parser byte budget")
    with context.artifacts.open(artifact.key) as stream:
        text = stream.read(64 * 1024 * 1024 + 1).decode("utf-8-sig")
    transcript = (
        from_asr_export(
            json.loads(text), params.asset_id, params.transcript_id, engine=params.engine
        )
        if params.format == "asr"
        else parse_timed_text(text, params.asset_id, params.transcript_id, engine=params.engine)
    )
    return PreparedResult(
        records=[
            RecordWrite("transcript", transcript.model_dump(mode="json"), params.expected_revision)
        ],
        artifacts=[artifact],
        summary={"cost_status": "unpriced_local", "identity_confirmed": False},
    )


def validate_localize(ledger: Any, job: JobRequest) -> None:
    params = Localize.model_validate(job.parameters)
    bound(ledger, job, "speaker_profile", params.profile_id)
    bound(ledger, job, "transcript", params.transcript_id)
    if job.artifacts:
        raise ValueError("Localization reads its versioned transcript, not a replacement artifact")


def prepare_localize(context: WorkContext, job: JobRequest) -> PreparedResult:
    params = Localize.model_validate(job.parameters)
    payload = derive_localization(
        context.ledger, params.profile_id, params.transcript_id, params.config, []
    )
    payload["id"] = "localization-" + context.job_id[4:]
    return PreparedResult(
        records=[RecordWrite("localization_run", payload)],
        summary={"cost_status": "unpriced_local", "identity_confirmed": False},
    )


def validate_clip(ledger: Any, job: JobRequest) -> None:
    params = Clip.model_validate(job.parameters)
    asset = media_rights(
        ledger, job, params.asset_id, ("store_media", "derive_clip", "process_audio")
    )
    if set(job.artifacts) != {"media"} or job.artifacts["media"].sha256 != asset["content_sha256"]:
        raise ValueError("Media artifact does not match the registered source")
    clip_plan(params.start_ms, params.end_ms, asset["duration_ms"], params.padding_ms)


def prepare_clip(context: WorkContext, job: JobRequest) -> PreparedResult:
    params = Clip.model_validate(job.parameters)
    asset = bound(context.ledger, job, "asset", params.asset_id)
    grant = RightsGrant.model_validate(
        context.ledger.store.get("rights", asset["rights_id"])["payload"]
    )
    artifact = Artifact(**job.artifacts["media"].model_dump())
    plan = clip_plan(params.start_ms, params.end_ms, asset["duration_ms"], params.padding_ms)
    with context.artifacts.materialize(artifact, suffix=".media") as source:
        destination = source.parent / "clip.wav"
        context.check_cancelled()
        local_clip(source, destination, plan, grant, source.parent)
        context.check_cancelled()
        with destination.open("rb") as result:
            clipped = context.artifacts.put(result)
    manifest = {
        "format": "worker-clip-v1",
        "source": artifact.as_dict(),
        "clip": clipped.as_dict(),
        "asset_id": params.asset_id,
        "plan": plan,
        "source_start_ms": plan["context_start_ms"],
        "identity_confirmed": False,
        "publication_authorized": False,
    }
    receipt = context.artifacts.put_bytes(canonical_json(manifest).encode())
    return PreparedResult(
        artifacts=[artifact, clipped, receipt],
        summary={"manifest": receipt.key, "cost_status": "unpriced_local"},
    )


def validate_jev(ledger: Any, job: JobRequest) -> None:
    from statement_ledger.infrastructure.providers.jev import authorize_bindings, validate_questions

    params = JevDecision.model_validate(job.parameters)
    request = params.request
    expected = {"purpose", "question_version", "state", "questions", "input_ids", "bindings"}
    if set(request) != expected:
        raise ValueError("Unexpected Jev request fields")
    if not request["bindings"]:
        raise ValueError("Jev needs source-bound inputs")
    for item in request["bindings"]:
        bound(ledger, job, item["kind"], item["id"])
    authorize_bindings(ledger, request["bindings"])
    validate_questions(request["questions"])


def prepare_jev(context: WorkContext, job: JobRequest) -> PreparedResult:
    from statement_ledger.infrastructure.providers.jev import (
        ENDPOINT,
        VALIDATOR_VERSION,
        JevClient,
        JevConfig,
        cache_eligible,
        find_cached_decision,
    )

    if not context.settings.jev_enabled:
        raise ValueError("Jev is disabled")
    params = JevDecision.model_validate(job.parameters)
    request = params.request
    model = context.settings.jev_model
    key = digest({**request, "endpoint": ENDPOINT, "model": model, "validator": VALIDATOR_VERSION})
    config = JevConfig(model=model, max_attempts=1)
    operation_id = "jev-" + uuid.uuid4().hex
    context.check_cancelled()
    journal = context.operations
    # Owner-authorized refresh bypasses old results; the journal consumes permission atomically.
    if not journal.retry_authorized(key, "typesafe"):
        cached = find_cached_decision(context.ledger, key, config)
        if cached is not None:
            return PreparedResult(
                records=[RecordWrite("decision_run", cached["payload"], cached["revision"])],
                summary={"cache_hit": True, "cost_status": "reused"},
            )
        recovered = journal.recover_decision(key, "typesafe")
        if recovered is not None and cache_eligible(recovered, config):
            return PreparedResult(
                records=[RecordWrite("decision_run", recovered)],
                summary={"cache_hit": True, "cost_status": "reused"},
            )
    # An alias/expired/unrecoverable prior result is not permission to spend again.
    credential = LocalSecrets().value("TYPESAFE_API_KEY")
    context.check_cancelled()
    journal.begin(
        operation_id,
        key,
        "typesafe",
        estimate_micro_usd=context.settings.remote_estimate_micro_usd,
        budget_micro_usd=context.settings.remote_budget_micro_usd,
    )
    submitted = False
    try:

        def capture(attempt: int, status: int | None, body: bytes, truncated: bool) -> str:
            return context.capture_response(
                key,
                attempt,
                status,
                body,
                truncated,
                {**request, "endpoint": ENDPOINT, "model": model, "validator": VALIDATOR_VERSION},
            )

        with JevClient(credential, config=config) as client:
            # Last check before any potentially paid external effect.
            context.check_cancelled()
            submitted = True
            result = client.evaluate(request["state"], request["questions"], capture=capture)
        if result["status"] == "unavailable":
            journal.unknown(operation_id)
            raise OperationBlocked(
                "Remote outcome is unavailable; inspect receipts before recovery"
            )
        payload = {
            "id": "decision-" + uuid.uuid4().hex,
            "purpose": request["purpose"],
            "request_hash": key,
            "model_requested": model,
            "question_version": request["question_version"],
            "questions": request["questions"],
            "state_sha256": digest(request["state"]),
            "bindings": request["bindings"],
            "input_ids": request["input_ids"],
            "captured_at": now().isoformat(),
            **result,
        }
        # Persist the full successful proposal before its fenced canonical commit. A busy
        # commit or process restart can recover this result without another provider call.
        journal.complete(
            operation_id,
            {
                "usage": result["usage"],
                "receipt_ids": result["receipt_ids"],
                "decision": payload,
            },
        )
        return PreparedResult(
            records=[RecordWrite("decision_run", payload)],
            summary={"operation_id": operation_id, "cache_hit": False, "cost_status": "unknown"},
        )
    except BaseException as exc:
        if not submitted:
            journal.cancel_unsent(operation_id)
            raise
        try:
            journal.unknown(operation_id)
        except Exception:
            # A retained 'started' reservation is also ambiguous and blocks re-spending.
            pass
        if isinstance(exc, (LeaseLost, OperationBlocked, KeyboardInterrupt, SystemExit)):
            raise
        raise OperationBlocked("Remote attempt requires receipt reconciliation") from None


def validate_transcribe(ledger: Any, job: JobRequest) -> None:
    params = Transcribe.model_validate(job.parameters)
    asset = media_rights(
        ledger, job, params.asset_id, ("process_audio", "store_text", "store_media")
    )
    if set(job.artifacts) != {"media"} or job.artifacts["media"].sha256 != asset["content_sha256"]:
        raise ValueError("Transcription requires the registered media artifact")


def prepare_transcribe(context: WorkContext, job: JobRequest) -> PreparedResult:
    from statement_ledger.infrastructure.providers.local_model import (
        model_manifest,
        transcribe_provisioned,
    )

    params = Transcribe.model_validate(job.parameters)
    directory = context.settings.data_root / "models" / context.settings.speech_model_name
    manifest = model_manifest(directory, params.model_manifest_sha256, verify_files=True)
    artifact = Artifact(**job.artifacts["media"].model_dump())
    with context.artifacts.materialize(artifact, suffix=".media") as source:
        context.check_cancelled()
        raw = transcribe_provisioned(source, directory, context.settings.speech_compute_type)
        context.check_cancelled()
    model_manifest(directory, params.model_manifest_sha256)
    raw["model_revision"] = manifest["revision"]
    raw["model_manifest_sha256"] = params.model_manifest_sha256
    receipt = context.artifacts.put_bytes(canonical_json(raw).encode())
    transcript = from_asr_export(
        raw, params.asset_id, params.transcript_id, engine="faster-whisper:" + manifest["revision"]
    )
    return PreparedResult(
        records=[
            RecordWrite("transcript", transcript.model_dump(mode="json"), params.expected_revision)
        ],
        artifacts=[artifact, receipt],
        summary={
            "identity_confirmed": False,
            "model_manifest_sha256": params.model_manifest_sha256,
            "cost_status": "unpriced_local",
            "raw_asr": receipt.key,
        },
    )


def handlers() -> dict[str, Handler]:
    return {
        "speech.transcribe": Handler(
            "speech.transcribe",
            1,
            "gpu",
            validate_transcribe,
            prepare_transcribe,
            frozenset({"transcript"}),
        ),
        "transcript.import": Handler(
            "transcript.import",
            1,
            "cpu",
            validate_import,
            prepare_import,
            frozenset({"transcript"}),
        ),
        "speech.localize": Handler(
            "speech.localize",
            1,
            "cpu",
            validate_localize,
            prepare_localize,
            frozenset({"localization_run"}),
        ),
        "media.clip": Handler("media.clip", 1, "cpu", validate_clip, prepare_clip, frozenset()),
        "jev.decision": Handler(
            "jev.decision", 1, "cpu", validate_jev, prepare_jev, frozenset({"decision_run"})
        ),
    }
