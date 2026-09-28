"""PR #1 review regressions: mocked provider, fictional turns, real local queue."""

from __future__ import annotations

import copy
import json
import sqlite3
from dataclasses import replace
from pathlib import Path

import httpx
import pytest

from statement_ledger.application.acceleration_demo import seed_acceleration
from statement_ledger.application.handlers import handlers
from statement_ledger.application.proof import make_request
from statement_ledger.contracts.identity import job_content
from statement_ledger.contracts.runtime import JobRequest
from statement_ledger.infrastructure.operations import OperationBlocked, OperationJournal
from statement_ledger.infrastructure.providers import jev
from statement_ledger.infrastructure.queue import JobRequiresRequeue, RuntimeQueue
from statement_ledger.infrastructure.secrets import LocalSecrets
from statement_ledger.infrastructure.settings import Settings
from statement_ledger.infrastructure.worker import Handler, PreparedResult, RecordWrite, Worker


@pytest.fixture
def remote_case(ledger, tmp_path, monkeypatch):
    seed_acceleration(ledger)
    settings = Settings(
        data_root=tmp_path,
        db_path=Path(ledger.store.path),
        jev_enabled=True,
        remote_estimate_micro_usd=10,
        remote_budget_micro_usd=100,
    )
    references = [("transcript", "style-heldout-transcript"), ("speaker_profile", "profile-demo")]
    request = {
        "purpose": "speaker_localization",
        "question_version": "review-fixture-v1",
        "state": "Fictional testing passage.",
        "questions": {"q": {"type": "noul", "instructions": "Is this the supplied pattern?"}},
        "bindings": [
            {"kind": k, "id": i, "revision": ledger.store.get(k, i)["revision"]}
            for k, i in references
        ],
        "input_ids": ["fixture-window"],
    }
    job = make_request(ledger, settings, "jev.decision", {"request": request}, references)
    calls = []
    real_client = jev.JevClient

    def respond(req):
        calls.append(req)
        return httpx.Response(
            200,
            json={
                "model": settings.jev_model,
                "answers": {"q": {"type": "noul", "noul": 0.7}},
                "usage": {"input_tokens": 8, "output_tokens": 1},
            },
        )

    monkeypatch.setattr(
        jev,
        "JevClient",
        lambda key, **kw: real_client(key, transport=httpx.MockTransport(respond), **kw),
    )
    monkeypatch.setattr(LocalSecrets, "value", lambda *_: "synthetic")
    return ledger, settings, job, calls


@pytest.mark.parametrize("mode", ["cancel", "expire"])
def test_cancelled_after_claim_never_reserves_or_calls(remote_case, mode):
    ledger, settings, job, calls = remote_case
    queue = RuntimeQueue(ledger.store)
    jid = queue.submit(job)
    registered = handlers()
    original = registered[job.handler]

    def cancel_at_validation(read, request):
        original.validate(read, request)
        if mode == "cancel":
            queue.cancel(jid)
        else:
            ledger.store.db.execute("UPDATE work_jobs SET lease_until=0 WHERE id=?", (jid,))

    registered[job.handler] = replace(original, validate=cancel_at_validation)
    result = Worker(ledger, settings, registered, heartbeat=False).run_once()
    assert result["state"] == ("cancelled" if mode == "cancel" else "running")
    assert not calls and not OperationJournal(ledger.store).list()


def test_cancel_immediately_before_reservation_never_spends(remote_case, monkeypatch):
    ledger, settings, job, calls = remote_case
    jid = RuntimeQueue(ledger.store).submit(job)

    def credentials(_self, _name):
        RuntimeQueue(ledger.store).cancel(jid)
        return "synthetic"

    monkeypatch.setattr(LocalSecrets, "value", credentials)
    assert Worker(ledger, settings, handlers(), heartbeat=False).run_once()["state"] == "cancelled"
    assert not calls and not OperationJournal(ledger.store).list()


def test_cancel_after_reservation_before_network_is_known_zero(remote_case, monkeypatch):
    ledger, settings, job, calls = remote_case
    jid = RuntimeQueue(ledger.store).submit(job)
    begin = OperationJournal.begin

    def reserve_then_cancel(self, *args, **kwargs):
        begin(self, *args, **kwargs)
        RuntimeQueue(ledger.store).cancel(jid)

    monkeypatch.setattr(OperationJournal, "begin", reserve_then_cancel)
    assert Worker(ledger, settings, handlers(), heartbeat=False).run_once()["state"] == "cancelled"
    receipt = OperationJournal(ledger.store).list()[0]
    assert receipt["state"] == "cancelled" and receipt["actual_micro_usd"] == 0 and not calls


def test_retry_policy_and_input_order_do_not_duplicate_payment(remote_case):
    ledger, settings, job, calls = remote_case
    queue = RuntimeQueue(ledger.store)
    first = queue.submit(job)
    changed = job.model_copy(
        update={"run_id": "another-run", "max_attempts": 9, "inputs": list(reversed(job.inputs))}
    )
    assert queue.submit(changed) == first
    assert Worker(ledger, settings, handlers(), heartbeat=False).run_once()["state"] == "succeeded"
    report = queue.submit_with_status(changed)
    assert report["job_id"] == first and report["state"] == "succeeded" and report["reused"]
    assert len(calls) == 1
    assert len(OperationJournal(ledger.store).list()) == 1
    assert Worker(ledger, settings, handlers(), heartbeat=False).run_once() is None


def test_cross_job_content_cache_is_shared(remote_case):
    ledger, settings, job, calls = remote_case
    first = Worker(ledger, settings, handlers(), heartbeat=False)
    first.queue.submit(job)
    assert first.run_once()["state"] == "succeeded"
    # A larger budget changes the job configuration, but not the provider request.
    other_settings = settings.model_copy(update={"remote_budget_micro_usd": 200})
    other = job.model_copy(update={"config_sha256": other_settings.execution_hash()})
    assert first.queue.identity(other) != first.queue.identity(job)
    first.queue.submit(other)
    result = Worker(ledger, other_settings, handlers(), heartbeat=False).run_once()
    assert result["state"] == "succeeded" and result["result"]["cache_hit"]
    assert len(calls) == 1 and len(ledger.store.all("decision_run")) == 1
    assert ledger.store.all("decision_run")[0]["revision"] == 1


def test_positional_provider_bindings_not_reordered_by_job_identity(remote_case):
    _, _, job, _ = remote_case
    parameters = copy.deepcopy(job.parameters)
    parameters["request"]["bindings"].reverse()
    reversed_roles = job.model_copy(update={"parameters": parameters})
    assert job_content(job) != job_content(reversed_roles)
    request = job.parameters["request"]
    assert job_content(job)["parameters"]["request"]["bindings"] == request["bindings"]


def test_completed_remote_proposal_recovers_after_busy_commit(remote_case, monkeypatch):
    ledger, settings, job, calls = remote_case
    worker = Worker(ledger, settings, handlers(), heartbeat=False)
    jid = worker.queue.submit(job)
    write = ledger.store.write
    failed = []

    def fail_first_decision(kind, *args, **kwargs):
        if kind == "decision_run" and not failed:
            failed.append(True)
            raise sqlite3.OperationalError("database is locked")
        return write(kind, *args, **kwargs)

    monkeypatch.setattr(ledger.store, "write", fail_first_decision)
    assert worker.run_once()["state"] == "pending"
    assert not ledger.store.all("decision_run")
    ledger.store.db.execute("UPDATE work_jobs SET available=0 WHERE id=?", (jid,))
    assert worker.run_once()["state"] == "succeeded"
    assert len(calls) == 1 and len(ledger.store.all("decision_run")) == 1


def test_ambiguous_paid_call_never_auto_retries_even_after_requeue(remote_case, monkeypatch):
    ledger, settings, job, calls = remote_case
    real_client = jev.JevClient

    # Override the existing fake with a bounded transport timeout; still no network.
    def unavailable(*_args, **_kw):
        class Client:
            def __enter__(self):
                return self

            def __exit__(self, *_):
                pass

            def evaluate(self, *_args, **_kw):
                calls.append("mock-timeout")
                raise httpx.ReadTimeout("synthetic")

        return Client()

    monkeypatch.setattr(jev, "JevClient", unavailable)
    worker = Worker(ledger, settings, handlers(), heartbeat=False)
    jid = worker.queue.submit(job)
    assert worker.run_once()["state"] == "blocked"
    assert worker.run_once() is None
    report = worker.queue.submit_with_status(job)
    assert report["state"] == "blocked" and report["requeue_required"]
    with pytest.raises(JobRequiresRequeue):
        worker.queue.submit(job)
    worker.queue.requeue(jid, reason="Inspect operation; do not authorize another paid call")
    assert worker.run_once()["state"] == "blocked"
    assert len(calls) == 1 and OperationJournal(ledger.store).list()[0]["state"] == "unknown"
    assert real_client is not None


@pytest.mark.parametrize(
    "error",
    [
        httpx.ConnectError("synthetic"),
        httpx.ReadTimeout("synthetic"),
        sqlite3.OperationalError("database is locked"),
        sqlite3.OperationalError("database table is locked"),
    ],
)
def test_non_paid_transient_work_retries_with_audit(ledger, tmp_path, error):
    settings = Settings(data_root=tmp_path, db_path=Path(ledger.store.path))
    attempts = []

    def prepare(_context, _request):
        attempts.append(1)
        if len(attempts) == 1:
            raise error
        return PreparedResult(
            records=[RecordWrite("person", {"id": "synthetic-retry", "display_name": "Fictional"})]
        )

    worker = Worker(
        ledger,
        settings,
        {
            "test.retry": Handler(
                "test.retry", 1, "cpu", lambda *_: None, prepare, frozenset({"person"})
            )
        },
        heartbeat=False,
    )
    jid = worker.queue.submit(
        JobRequest(handler="test.retry", config_sha256=settings.execution_hash())
    )
    result = worker.run_once()
    assert result["state"] == "pending" and result["error_code"] == "retryable_work"
    ledger.store.db.execute("UPDATE work_jobs SET available=0 WHERE id=?", (jid,))
    assert worker.run_once()["state"] == "succeeded" and len(attempts) == 2
    assert ledger.store.verify_audit()["valid"]


def test_requeue_preserves_attempt_history_and_does_not_retry_validation(ledger, tmp_path):
    settings = Settings(data_root=tmp_path, db_path=Path(ledger.store.path))

    def prepare(*_):
        raise ValueError("deterministic bad input")

    worker = Worker(
        ledger,
        settings,
        {"test.invalid": Handler("test.invalid", 1, "cpu", lambda *_: None, prepare, frozenset())},
        heartbeat=False,
    )
    request = JobRequest(
        handler="test.invalid", config_sha256=settings.execution_hash(), max_attempts=1
    )
    jid = worker.queue.submit(request)
    assert worker.run_once()["state"] == "failed"
    with pytest.raises(JobRequiresRequeue):
        worker.queue.submit(request)
    with pytest.raises(ValueError):
        worker.queue.requeue(jid, reason=" ")
    retried = worker.queue.requeue(
        jid, reason="Synthetic operator correction", additional_attempts=1
    )
    assert retried["attempts"] == 1 and retried["max_attempts"] == 2
    assert worker.run_once()["state"] == "failed"
    assert [
        r[0] for r in ledger.store.db.execute("SELECT ordinal FROM work_attempts ORDER BY ordinal")
    ] == [1, 2]
    assert any(
        json.loads(r[0])["type"] == "work.requeued"
        for r in ledger.store.db.execute("SELECT event FROM audit")
    )


def test_content_reservation_is_atomic_across_operation_ids(ledger, tmp_path):
    from concurrent.futures import ThreadPoolExecutor

    from statement_ledger.infrastructure.sqlite_store import Store

    def reserve(name):
        store = Store(ledger.store.path)
        try:
            OperationJournal(store).begin(
                name, "a" * 64, "synthetic", estimate_micro_usd=1, budget_micro_usd=10
            )
            return True
        except OperationBlocked:
            return False
        finally:
            store.close()

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(reserve, ["one", "two"]))
    assert sorted(results) == [False, True]
    assert len(OperationJournal(ledger.store).list()) == 1


def test_blocked_job_recovers_only_after_explicit_requeue(ledger, tmp_path):
    settings = Settings(data_root=tmp_path, db_path=Path(ledger.store.path))
    blocked = [True]

    def prepare(_context, _request):
        if blocked[0]:
            raise OperationBlocked("Synthetic operator prerequisite")
        return PreparedResult(summary={"recovered": True})

    worker = Worker(
        ledger,
        settings,
        {"test.blocked": Handler("test.blocked", 1, "cpu", lambda *_: None, prepare, frozenset())},
        heartbeat=False,
    )
    jid = worker.queue.submit(
        JobRequest(handler="test.blocked", config_sha256=settings.execution_hash())
    )
    assert worker.run_once()["state"] == "blocked"
    blocked[0] = False
    assert worker.run_once() is None
    worker.queue.requeue(jid, reason="Synthetic prerequisite repaired")
    result = worker.run_once()
    assert result["state"] == "succeeded" and result["result"]["recovered"]
