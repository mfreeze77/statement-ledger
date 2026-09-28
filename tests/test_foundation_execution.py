"""Failure and integration checks for the worker and operational interfaces."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from statement_ledger.application.api import create_app
from statement_ledger.application.proof import make_request, prove
from statement_ledger.contracts.runtime import JobRequest
from statement_ledger.infrastructure.migrations import migrate
from statement_ledger.infrastructure.providers.local_model import model_manifest
from statement_ledger.infrastructure.queue import RuntimeQueue
from statement_ledger.infrastructure.settings import Settings, load_settings
from statement_ledger.infrastructure.worker import (
    Handler,
    PreparedResult,
    RecordWrite,
    RetryableWork,
    Worker,
)


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="Requires actual FFmpeg")
def test_integrated_worker_restart_correction_restore(tmp_path):
    result = prove(tmp_path / "workspace")
    assert result["restore_verified"] and result["immediate_invalidation"] and result["audit_valid"]
    assert result["provider_calls"] == 0 and result["registered_artifacts"] >= 4


def test_heartbeat_preserves_long_work(ledger, tmp_path):
    settings = Settings(
        data_root=tmp_path, db_path=Path(ledger.store.path), lease_seconds=3, heartbeat_seconds=0.1
    )

    def prepare(context, request):
        time.sleep(3.2)
        context.check_cancelled()
        return PreparedResult(summary={"long_work": True})

    worker = Worker(
        ledger,
        settings,
        {"test.slow": Handler("test.slow", 1, "cpu", lambda *_: None, prepare, frozenset())},
    )
    request = JobRequest(handler="test.slow", config_sha256=settings.execution_hash())
    worker.queue.submit(request)
    assert worker.run_once()["state"] == "succeeded"


def test_cancel_during_prepare_cannot_publish(ledger, tmp_path):
    settings = Settings(data_root=tmp_path, db_path=Path(ledger.store.path))

    def prepare(context, request):
        RuntimeQueue(ledger.store).cancel(context.job_id)
        return PreparedResult(
            records=[
                RecordWrite(
                    "person",
                    {"id": "never-written", "display_name": "Synthetic", "synthetic": True},
                )
            ]
        )

    worker = Worker(
        ledger,
        settings,
        {
            "test.cancel": Handler(
                "test.cancel", 1, "cpu", lambda *_: None, prepare, frozenset({"person"})
            )
        },
        heartbeat=False,
    )
    worker.queue.submit(JobRequest(handler="test.cancel", config_sha256=settings.execution_hash()))
    assert worker.run_once()["state"] == "cancelled"
    assert ledger.store.all("person") == []


def test_retry_and_attempt_exhaustion(ledger, tmp_path):
    settings = Settings(data_root=tmp_path, db_path=Path(ledger.store.path))

    def fail(context, request):
        raise RetryableWork("safe fixture failure")

    worker = Worker(
        ledger,
        settings,
        {"test.retry": Handler("test.retry", 1, "cpu", lambda *_: None, fail, frozenset())},
        heartbeat=False,
    )
    identity = worker.queue.submit(
        JobRequest(handler="test.retry", config_sha256=settings.execution_hash(), max_attempts=2)
    )
    assert worker.run_once()["state"] == "pending"
    ledger.store.db.execute("UPDATE work_jobs SET available=0 WHERE id=?", (identity,))
    result = worker.run_once()
    assert result["state"] == "failed" and result["attempts"] == 2
    assert worker.run_once() is None


def test_outbox_dispatch_failure_rolls_back_job_and_ack(ledger, tmp_path):
    queue = RuntimeQueue(ledger.store)
    request = JobRequest(handler="test.event", config_sha256="0" * 64)
    queue.submit(request)
    ledger.store.db.execute(
        "INSERT INTO outbox(event) VALUES(?)",
        ('{"type":"work.requested","job_id":"invalid","request":{}}',),
    )
    with pytest.raises(ValueError):
        queue.dispatch()
    assert ledger.store.db.execute("SELECT count(*) FROM work_jobs").fetchone()[0] == 0
    assert (
        ledger.store.db.execute("SELECT count(*) FROM outbox WHERE state='pending'").fetchone()[0]
        == 2
    )


def test_provider_rights_revoked_before_commit(seeded, tmp_path):
    settings = Settings(data_root=tmp_path, db_path=Path(seeded.store.path))

    def prepare(context, request):
        rights = seeded.store.get("rights", "demo-rights")
        payload = rights["payload"]
        payload["allowed"] = ["discover"]
        seeded.put("rights", payload, rights["revision"])
        return PreparedResult(
            records=[
                RecordWrite(
                    "person",
                    {"id": "should-not-exist", "display_name": "Synthetic", "synthetic": True},
                )
            ]
        )

    worker = Worker(
        seeded,
        settings,
        {
            "test.revoke": Handler(
                "test.revoke", 1, "cpu", lambda *_: None, prepare, frozenset({"person"})
            )
        },
        heartbeat=False,
    )
    worker.queue.submit(
        make_request(seeded, settings, "test.revoke", {}, [("asset", "asset-original")])
    )
    assert worker.run_once()["error_code"] == "stale_input"
    assert all(row["id"] != "should-not-exist" for row in seeded.store.all("person"))


def test_configuration_failure_never_echoes_input(tmp_path):
    file = tmp_path / "config.toml"
    secret = "sensitive-example-not-a-key"
    file.write_text('[statement_ledger]\nport="' + secret + '"\n')
    with pytest.raises(ValueError) as error:
        load_settings(config_file=file, environ={})
    assert secret not in str(error.value)


def test_models_need_explicit_immutable_manifest(tmp_path):
    (tmp_path / "model.bin").write_bytes(b"not real weights")
    manifest = {
        "format": 1,
        "engine": "faster-whisper",
        "revision": "synthetic",
        "files": {"model.bin": hashlib.sha256(b"not real weights").hexdigest()},
    }
    raw = json.dumps(manifest).encode()
    (tmp_path / "manifest.json").write_bytes(raw)
    digest = hashlib.sha256(raw).hexdigest()
    assert model_manifest(tmp_path, digest, verify_files=True)["revision"] == "synthetic"
    (tmp_path / "model.bin").write_bytes(b"changed")
    with pytest.raises(ValueError, match="checksum"):
        model_manifest(tmp_path, digest, verify_files=True)
    with pytest.raises(ValueError, match="changed"):
        model_manifest(tmp_path, "0" * 64)


def test_job_api_is_authenticated_and_typed(tmp_path):
    settings = Settings(data_root=tmp_path)
    migrate(settings.database)
    token = "synthetic-test-token-not-for-deployment" * 2
    app = create_app(settings=settings, token=token)
    with TestClient(app) as client:
        assert client.get("/readyz").status_code == 200
        assert client.get("/api/jobs").status_code == 401
        auth = {"Authorization": "Bearer " + token}
        assert client.get("/api/jobs", headers=auth).status_code == 200
        assert (
            client.post("/api/jobs", headers=auth, json={"handler": "unknown"}).status_code == 422
        )
        assert token not in client.get("/api/runtime/config", headers=auth).text


def test_import_boundary_gate_rejects_deliberate_sibling_import(tmp_path):
    spec = importlib.util.spec_from_file_location(
        "boundary_gate", Path(__file__).resolve().parents[1] / "scripts/check-boundaries.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    path = tmp_path / "statement_ledger/pillars/claims/bad.py"
    path.parent.mkdir(parents=True)
    path.write_text("from statement_ledger.pillars.speech import profiles\n")
    assert module.check(tmp_path)
    path.write_text("from statement_ledger import speech\n")
    assert module.check(tmp_path)
    path.write_text("from statement_ledger.pillars import speech\n")
    assert module.check(tmp_path)


def test_cancellation_before_dispatch_is_durable(ledger):
    queue = RuntimeQueue(ledger.store)
    request = JobRequest(handler="test.pending", config_sha256="0" * 64)
    identity = queue.submit(request)
    queue.cancel(identity)
    queue.dispatch()
    assert queue.get(identity)["state"] == "cancelled"
    assert queue.claim() is None


def test_unregistered_artifacts_cannot_enter_a_pending_backup(ledger):
    from statement_ledger.contracts.runtime import ArtifactInput

    queue = RuntimeQueue(ledger.store)
    request = JobRequest(
        handler="test.artifact",
        config_sha256="0" * 64,
        artifacts={"media": ArtifactInput(key="sha256/aa/" + "a" * 64, sha256="a" * 64, size=10)},
    )
    with pytest.raises(ValueError, match="registered"):
        queue.submit(request)
    assert ledger.store.db.execute("SELECT count(*) FROM outbox").fetchone()[0] == 0


def test_doctor_exit_status_requires_ready_schema(tmp_path, capsys):
    from statement_ledger.application.cli import main

    path = tmp_path / "uninitialized.sqlite3"
    assert main(["--db", str(path), "doctor"]) == 2
    assert '"schema_ready": false' in capsys.readouterr().out
