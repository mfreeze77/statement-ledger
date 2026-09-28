"""Review regressions for live opt-in, credential transport, retry UI and leases."""

from __future__ import annotations

import argparse
import json
import logging
import threading
import time
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace

import httpx
import pytest
from fastapi.testclient import TestClient

from statement_ledger.application.api import create_app
from statement_ledger.application.runtime import add_commands, execute
from statement_ledger.contracts.runtime import ArtifactInput, JobRequest
from statement_ledger.infrastructure.artifacts import LocalArtifactStore
from statement_ledger.infrastructure.migrations import migrate
from statement_ledger.infrastructure.queue import RuntimeQueue
from statement_ledger.infrastructure.settings import CONTROL_ENV, Settings, load_settings
from statement_ledger.infrastructure.sqlite_store import Store
from statement_ledger.infrastructure.worker import Handler, PreparedResult, Worker
from statement_ledger.pillars.discovery.http import (
    FactCheckClient,
    SourceError,
    SourceUnavailable,
    YouTubeClient,
)


def test_non_ascii_authorization_is_401_not_500(tmp_path):
    settings = Settings(data_root=tmp_path)
    migrate(settings.database)
    with TestClient(create_app(settings=settings, token="synthetic-test-only" * 3)) as client:
        response = client.get("/api/jobs", headers=[(b"Authorization", b"Bearer \xff\xfe")])
        assert response.status_code == 401


def test_google_credentials_only_in_headers_never_urls_or_info_logs(caplog):
    caplog.set_level(logging.INFO, logger="httpx")
    key = "synthetic-credential-not-for-deployment"
    requests = []

    def respond(req):
        requests.append(req)
        assert req.headers["X-goog-api-key"] == key
        assert "key" not in req.url.params and key not in str(req.url)
        return httpx.Response(
            200,
            json={
                "items": [{"contentDetails": {"relatedPlaylists": {"uploads": "fixture"}}}],
                "claims": [],
            },
        )

    transport = httpx.MockTransport(respond)
    with YouTubeClient(key, transport=transport) as client:
        client.search("synthetic")
        client.uploads_playlist("fixture")
        client.playlist("fixture")
        client.videos(["fixture"])
    with FactCheckClient(key, transport=transport) as client:
        client.search("synthetic")
    assert len(requests) == 5
    assert key not in caplog.text and "key=" not in caplog.text


@pytest.mark.parametrize("value", ["", "0", "1"])
def test_live_control_environment_is_registered_and_offline_startup_safe(tmp_path, value):
    assert "SL_RUN_LIVE" in CONTROL_ENV
    settings = load_settings(environ={"SL_RUN_LIVE": value, "SL_DATA_ROOT": str(tmp_path)})
    assert not settings.jev_enabled
    migrate(settings.database)
    with TestClient(create_app(settings=settings, token="synthetic" * 8)) as client:
        assert client.get("/readyz").status_code == 200
    assert "SL_RUN_LIVE=" in (Path(__file__).parents[1] / ".env.example").read_text()


def test_submit_terminal_report_and_requeue_api_and_cli(tmp_path):
    settings = Settings(data_root=tmp_path)
    migrate(settings.database)
    with _store(settings.database) as store:
        queue = RuntimeQueue(store)
        job = JobRequest(handler="test.manual", config_sha256=settings.execution_hash())
        jid = queue.submit(job)
        queue.dispatch()
        claimed = queue.claim()
        queue.fail(jid, claimed["lease_token"], "synthetic_failure")
        report = queue.submit_with_status(job)
        assert report == {
            "job_id": jid,
            "state": "failed",
            "reused": True,
            "requeue_required": True,
        }
    token = "synthetic-private-test" * 3
    with TestClient(create_app(settings=settings, token=token)) as client:
        path = "/api/jobs/" + jid + "/requeue"
        assert client.post(path, json={"reason": "test"}).status_code == 401
        auth = {"Authorization": "Bearer " + token}
        assert client.post(path, headers=auth, json={"reason": " "}).status_code == 422
        response = client.post(path, headers=auth, json={"reason": "synthetic correction"})
        assert response.status_code == 200 and response.json()["state"] == "pending"
    with _store(settings.database) as store:
        RuntimeQueue(store).cancel(jid)
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    add_commands(sub)
    args = parser.parse_args(["requeue-job", jid, "--reason", "synthetic CLI correction"])
    assert execute(args, settings)["state"] == "pending"


# Context wrapper preserves the normal explicit-close Store interface.


@contextmanager
def _store(path):
    store = Store(path)
    try:
        yield store
    finally:
        store.close()


def test_legacy_pending_identity_replayed_without_duplicate_work(ledger):
    request = JobRequest(handler="test.legacy", config_sha256="0" * 64)
    queue = RuntimeQueue(ledger.store)
    legacy_id = queue.legacy_identity(request)
    event = {
        "type": "work.requested",
        "contract_version": 1,
        "job_id": legacy_id,
        "request": request.model_dump(mode="json"),
    }
    ledger.store.db.execute("INSERT INTO outbox(event) VALUES(?)", (json.dumps(event),))
    changed = request.model_copy(update={"max_attempts": 9})
    assert queue.submit(changed) == legacy_id
    queue.dispatch()
    assert queue.submit(changed) == legacy_id and len(queue.list()) == 1
    assert queue.get(legacy_id)["max_attempts"] == request.max_attempts


def test_heartbeat_covers_slow_artifact_hash_before_gpu_prepare(ledger, tmp_path, monkeypatch):
    # GPU capability routing only: fake handler, no device, inference, credential or network.
    settings = Settings(
        data_root=tmp_path,
        db_path=Path(ledger.store.path),
        worker_capability="gpu",
        lease_seconds=3,
        heartbeat_seconds=0.1,
    )
    artifact = LocalArtifactStore(settings.artifacts).put_bytes(b"synthetic-media")
    ledger.store.db.execute(
        "INSERT INTO artifact_refs VALUES(?,?,?,?)",
        (artifact.key, artifact.sha256, artifact.size, time.time()),
    )
    prepared = []

    def prepare(_context, _job):
        prepared.append(1)
        return PreparedResult()

    worker = Worker(
        ledger,
        settings,
        {"test.gpu": Handler("test.gpu", 1, "gpu", lambda *_: None, prepare, frozenset())},
    )
    job = JobRequest(
        handler="test.gpu",
        capability="gpu",
        config_sha256=settings.execution_hash(),
        artifacts={"media": ArtifactInput(**artifact.as_dict())},
    )
    worker.queue.submit(job)
    original_verify = worker.artifacts.verify
    from statement_ledger.infrastructure import queue as queue_module

    # Only the queue clock is virtual. Thread scheduling may be arbitrarily slow;
    # ordering comes from events, not a 300ms race against real elapsed time.
    clock = [time.time()]
    initial_time = clock[0]
    monkeypatch.setattr(queue_module, "time", SimpleNamespace(time=lambda: clock[0]))
    hashing = threading.Event()
    renewed = threading.Event()
    original_heartbeat = RuntimeQueue.heartbeat

    def observed_heartbeat(self, job_id, token, **kwargs):
        assert hashing.wait(timeout=10), "Worker did not start hashing"
        if not renewed.is_set():
            clock[0] = initial_time + 2
        original_heartbeat(self, job_id, token, **kwargs)
        renewed.set()

    monkeypatch.setattr(RuntimeQueue, "heartbeat", observed_heartbeat)
    competitors = []

    def slow_verify(value):
        hashing.set()
        assert renewed.wait(timeout=10), "Heartbeat must run during input verification"
        clock[0] = initial_time + 3.1  # Initial lease expired; renewed lease remains live.
        with _store(ledger.store.path) as competing_store:
            competitors.append(RuntimeQueue(competing_store).claim("gpu", lease_seconds=3))
        original_verify(value)

    monkeypatch.setattr(worker.artifacts, "verify", slow_verify)
    assert worker.run_once()["state"] == "succeeded"
    assert competitors == [None]
    assert prepared == [1]


@pytest.mark.parametrize("status", [429, 503])
def test_actual_source_client_exhaustion_is_classified_retryable(ledger, tmp_path, status):
    settings = Settings(data_root=tmp_path, db_path=Path(ledger.store.path))

    def prepare(_context, _request):
        with YouTubeClient(
            "synthetic", retries=0, transport=httpx.MockTransport(lambda _: httpx.Response(status))
        ) as client:
            client.search("synthetic")
        return PreparedResult()

    worker = Worker(
        ledger,
        settings,
        {"test.source": Handler("test.source", 1, "cpu", lambda *_: None, prepare, frozenset())},
        heartbeat=False,
    )
    worker.queue.submit(JobRequest(handler="test.source", config_sha256=settings.execution_hash()))
    result = worker.run_once()
    assert result["state"] == "pending" and result["error_code"] == "retryable_work"


def test_source_rejection_is_not_transient():
    with YouTubeClient(
        "synthetic", retries=0, transport=httpx.MockTransport(lambda _: httpx.Response(401))
    ) as client:
        with pytest.raises(SourceError) as error:
            client.search("synthetic")
        assert not isinstance(error.value, SourceUnavailable)


def test_enqueue_api_reports_previously_cancelled_job(seeded, tmp_path):
    from statement_ledger.application.proof import make_request

    settings = Settings(data_root=tmp_path, db_path=Path(seeded.store.path))
    captions = LocalArtifactStore(settings.artifacts).put_bytes(b"WEBVTT\n")
    seeded.store.db.execute(
        "INSERT INTO artifact_refs VALUES(?,?,?,?)",
        (captions.key, captions.sha256, captions.size, time.time()),
    )
    job = make_request(
        seeded,
        settings,
        "transcript.import",
        {"asset_id": "asset-original", "transcript_id": "fixture-import", "format": "vtt"},
        [("asset", "asset-original")],
        {"transcript": ArtifactInput(**captions.as_dict())},
    )
    queue = RuntimeQueue(seeded.store)
    jid = queue.submit(job)
    queue.cancel(jid)
    token = "synthetic-test-token" * 3
    with TestClient(create_app(settings=settings, token=token)) as client:
        response = client.post(
            "/api/jobs",
            headers={"Authorization": "Bearer " + token},
            json=job.model_dump(mode="json"),
        )
    assert response.status_code == 200
    assert response.json()["state"] == "cancelled" and response.json()["requeue_required"]
    assert response.json()["job_id"] == jid
