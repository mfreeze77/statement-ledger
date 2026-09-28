"""Offline integrated foundation proof; fictional records and generated silence only."""

from __future__ import annotations

import io
import json
import time
import wave
from pathlib import Path
from typing import Any

from statement_ledger.application.acceleration_demo import seed_acceleration
from statement_ledger.application.handlers import handlers
from statement_ledger.application.ledger import Ledger
from statement_ledger.contracts.runtime import ArtifactInput, Binding, JobRequest
from statement_ledger.infrastructure.artifacts import LocalArtifactStore
from statement_ledger.infrastructure.backup import backup, restore
from statement_ledger.infrastructure.migrations import migrate
from statement_ledger.infrastructure.queue import RuntimeQueue
from statement_ledger.infrastructure.settings import Settings
from statement_ledger.infrastructure.sqlite_store import Store
from statement_ledger.infrastructure.worker import Worker


def make_request(
    ledger: Ledger,
    settings: Settings,
    handler: str,
    parameters: dict[str, Any],
    inputs: list[tuple[str, str]],
    artifacts: dict[str, ArtifactInput] | None = None,
) -> JobRequest:
    bindings = []
    for kind, record_id in inputs:
        row = ledger.store.get(kind, record_id)
        bindings.append(
            Binding(kind=kind, id=record_id, revision=row["revision"], record_hash=row["hash"])
        )
    return JobRequest(
        handler=handler,
        inputs=bindings,
        parameters=parameters,
        artifacts=artifacts or {},
        config_sha256=settings.execution_hash(),
        run_id="foundation-proof",
    )


def prove(root: Path) -> dict[str, Any]:
    if root.exists() and any(root.iterdir()):
        raise ValueError("Foundation proof requires an empty workspace")
    settings = Settings(data_root=root)
    settings.prepare_directories()
    migrate(settings.database)
    store = Store(settings.database)
    ledger = Ledger(store)
    ledger.settings = settings
    seed_acceleration(ledger)
    artifacts = LocalArtifactStore(settings.artifacts)
    stream = io.BytesIO()
    with wave.open(stream, "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(16000)
        audio.writeframes(b"\0\0" * 32000)
    media = artifacts.put_bytes(stream.getvalue())
    captions = artifacts.put_bytes(
        b"WEBVTT\n\n00:00:00.000 --> 00:00:01.000\nSynthetic workflow test only.\n"
    )
    for artifact in (media, captions):
        with store.transaction():
            store.db.execute(
                "INSERT OR IGNORE INTO artifact_refs VALUES(?,?,?,?)",
                (artifact.key, artifact.sha256, artifact.size, time.time()),
            )
    ledger.put(
        "asset",
        {
            "id": "proof-asset",
            "event_id": "event-1",
            "observation_id": "demo-show",
            "rights_id": "demo-rights",
            "url": "https://example.org/synthetic-proof",
            "duration_ms": 2000,
            "content_sha256": media.sha256,
        },
    )
    transcript_job = make_request(
        ledger,
        settings,
        "transcript.import",
        {"asset_id": "proof-asset", "transcript_id": "proof-transcript", "format": "vtt"},
        [("asset", "proof-asset")],
        {"transcript": ArtifactInput(**captions.as_dict())},
    )
    identity = RuntimeQueue(store).submit(transcript_job)
    store.close()  # Durable handoff survives closing and reopening the process state.
    store = Store(settings.database)
    ledger = Ledger(store)
    ledger.settings = settings
    worker = Worker(ledger, settings, handlers())
    imported = worker.run_once()
    if imported is None or imported["id"] != identity or imported["state"] != "succeeded":
        raise AssertionError("Transcript job did not complete")
    RuntimeQueue(store).submit(transcript_job)
    worker.run_once()
    if store.get("transcript", "proof-transcript")["revision"] != 1:
        raise AssertionError("Duplicate delivery created another canonical result")
    localize = make_request(
        ledger,
        settings,
        "speech.localize",
        {"profile_id": "profile-demo", "transcript_id": "style-heldout-transcript"},
        [("speaker_profile", "profile-demo"), ("transcript", "style-heldout-transcript")],
    )
    RuntimeQueue(store).submit(localize)
    planned = worker.run_once()
    if planned is None or planned["state"] != "succeeded":
        raise AssertionError("Localization did not complete")
    clip = make_request(
        ledger,
        settings,
        "media.clip",
        {"asset_id": "proof-asset", "start_ms": 500, "end_ms": 1500, "padding_ms": 0},
        [("asset", "proof-asset")],
        {"media": ArtifactInput(**media.as_dict())},
    )
    RuntimeQueue(store).submit(clip)
    clipped = worker.run_once()
    if clipped is None or clipped["state"] != "succeeded":
        raise AssertionError("Actual FFmpeg worker did not complete")
    with artifacts.open(clipped["result"]["manifest"]) as file:
        manifest = json.load(file)
    if manifest["source_start_ms"] != 500 or manifest["identity_confirmed"] is not False:
        raise AssertionError("Clip lost its source context or invented identity")
    before = store.get("review", "review-1")
    transcript = store.get("transcript", "transcript-asset-original")
    payload = transcript["payload"]
    payload["segments"][0]["text"] += " Synthetic correction."
    ledger.put("transcript", payload, transcript["revision"], actor="synthetic-reviewer")
    if before["stale"] or not store.get("review", "review-1")["stale"]:
        raise AssertionError("Correction did not synchronously invalidate the dependent review")
    audits = store.verify_audit()
    store.close()
    backup_path = root.parent / (root.name + "-backup")
    destination = root.parent / (root.name + "-restored")
    snapshot = backup(settings, backup_path)
    restored = restore(backup_path, destination)
    result = {
        "synthetic": True,
        "run_id": "foundation-proof",
        "transcript_job": identity,
        "localization_job": planned["id"],
        "clip_job": clipped["id"],
        "duplicate_revision": 1,
        "immediate_invalidation": True,
        "audit_valid": audits["valid"],
        "registered_artifacts": len(snapshot["artifacts"]),
        "restore_verified": restored["records_and_audit_verified"],
        "provider_calls": 0,
        "gpu_inference": False,
    }
    return result
