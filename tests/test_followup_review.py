"""PR #1 follow-up: owner recovery, single-use spend permission and shared cache policy.

All providers are mocked. No live opt-in, credentials, GPU or real person data.
"""

from __future__ import annotations

import argparse
import copy
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from pathlib import Path

import httpx
import pytest
import test_review_jobs as review_fixtures

from statement_ledger.application.handlers import handlers
from statement_ledger.application.operation_recovery import recover_jev_operation
from statement_ledger.application.runtime import add_commands, execute
from statement_ledger.contracts.models import now
from statement_ledger.core.util import digest
from statement_ledger.infrastructure.migrations import MigrationError, migrate
from statement_ledger.infrastructure.operations import OperationBlocked, OperationJournal
from statement_ledger.infrastructure.providers import jev
from statement_ledger.infrastructure.sqlite_store import Store
from statement_ledger.infrastructure.worker import Worker

remote_case = review_fixtures.remote_case


def historical_operation(case, *, operation_id="job-legacy", body=None, metadata_change=None):
    ledger, settings, job, calls = case
    metadata = {
        **copy.deepcopy(job.parameters["request"]),
        "endpoint": jev.ENDPOINT,
        "model": settings.jev_model,
        "validator": jev.VALIDATOR_VERSION,
    }
    key = digest(metadata)
    journal = OperationJournal(ledger.store)
    journal.begin(operation_id, key, "typesafe", estimate_micro_usd=10, budget_micro_usd=100)
    raw = (
        body
        if body is not None
        else json.dumps(
            {
                "model": settings.jev_model,
                "answers": {"q": {"type": "noul", "noul": 0.7}},
                "usage": {"input_tokens": 8, "output_tokens": 1},
            }
        ).encode()
    )
    if metadata_change:
        metadata.update(metadata_change)
    receipt_id = ledger.store.capture_provider_response(key, 1, 200, raw, False, metadata)
    journal.unknown(operation_id)
    journal.reconcile(operation_id, actual_micro_usd=7, evidence="Fictional billing evidence")
    return journal, operation_id, key, receipt_id


def audit_events(ledger):
    return [json.loads(row[0]) for row in ledger.store.db.execute("SELECT event FROM audit")]


def test_exact_main_read_instruction_restored():
    text = (Path(__file__).parents[1] / "AGENTS.md").read_text()
    assert (
        text.splitlines()[6]
        == "Read SPECIFICATION.md, docs/IMPLEMENTATION_STATUS.md, and the chosen ticket first."
    )
    assert "## Executable foundation rules" in text
    assert "## Rules for Codex (cloud agent)" in text


@pytest.mark.parametrize("operation_id", ["job-legacy", "decision-content-key"])
def test_reconciled_request_stays_blocked_without_owner_choice(remote_case, operation_id):
    ledger, settings, job, calls = remote_case
    journal, op, key, _receipt = historical_operation(remote_case, operation_id=operation_id)
    worker = Worker(ledger, settings, handlers(), heartbeat=False)
    jid = worker.queue.submit(job)
    assert worker.run_once()["state"] == "blocked"
    worker.queue.requeue(jid, reason="Inspect only, no new spend permission")
    assert worker.run_once()["state"] == "blocked"
    assert not calls and journal.recover_decision(key, "typesafe") is None
    assert journal.get(op)["actual_micro_usd"] == 7


def test_owner_recovers_retained_receipt_then_worker_reuses_without_payment(remote_case):
    ledger, settings, job, calls = remote_case
    journal, operation, key, receipt = historical_operation(remote_case)
    worker = Worker(ledger, settings, handlers(), heartbeat=False)
    jid = worker.queue.submit(job)
    assert worker.run_once()["state"] == "blocked"
    recovered = recover_jev_operation(
        ledger, operation, receipt, actor="local-owner", reason="Reviewed fictional raw receipt"
    )
    original_time = ledger.store.provider_receipt(receipt)["captured_at"]
    row = ledger.store.get("decision_run", recovered["decision_id"])
    assert row["payload"]["captured_at"].replace("Z", "+00:00") == original_time
    assert row["payload"]["latency_ms"] is None  # No invented historical latency.
    assert row["payload"]["answers"]["q"]["noul"] == 0.7
    assert journal.get(operation)["actual_micro_usd"] == 7
    assert journal.recover_decision(key, "typesafe")["id"] == row["id"]
    worker.queue.requeue(jid, reason="Recovered receipt validated")
    assert worker.run_once()["state"] == "succeeded"
    assert not calls
    event = [
        e for e in audit_events(ledger) if e["type"] == "provider.decision_recovered_by_owner"
    ][-1]
    assert event["actor"] == "local-owner" and event["reason"]
    assert ledger.store.verify_audit()["valid"]
    assert (
        recover_jev_operation(
            ledger, operation, receipt, actor="local-owner", reason="Repeat inspection"
        )["revision"]
        == 1
    )


@pytest.mark.parametrize(
    "invalid",
    [
        "body",
        "hash",
        "metadata",
        "status",
        "truncated",
        "old_time",
        "wrong_receipt_ids",
        "stale_input",
    ],
)
def test_receipt_recovery_rejects_invalid_or_inapplicable_evidence(remote_case, invalid):
    ledger, settings, job, calls = remote_case
    journal, operation, _key, receipt = historical_operation(remote_case)
    if invalid == "body":
        import hashlib

        bad = b"{}"
        ledger.store.db.execute(
            "UPDATE provider_receipts SET body=?,body_sha256=? WHERE id=?",
            (bad, hashlib.sha256(bad).hexdigest(), receipt),
        )
    elif invalid == "hash":
        ledger.store.db.execute(
            "UPDATE provider_receipts SET body=? WHERE id=?", (b"tampered", receipt)
        )
    elif invalid == "metadata":
        metadata = ledger.store.provider_receipt(receipt)["request_metadata"]
        metadata["state"] = "Different fictional source"
        ledger.store.db.execute(
            "UPDATE provider_receipts SET request_metadata=? WHERE id=?",
            (json.dumps(metadata), receipt),
        )
    elif invalid == "status":
        ledger.store.db.execute(
            "UPDATE provider_receipts SET http_status=503 WHERE id=?", (receipt,)
        )
    elif invalid == "truncated":
        ledger.store.db.execute("UPDATE provider_receipts SET truncated=1 WHERE id=?", (receipt,))
    elif invalid == "old_time":
        ledger.store.db.execute(
            "UPDATE provider_receipts SET captured_at=? WHERE id=?",
            ((now() - timedelta(days=2)).isoformat(), receipt),
        )
    elif invalid == "wrong_receipt_ids":
        ledger.store.db.execute(
            "UPDATE provider_operations SET usage=? WHERE id=?",
            (json.dumps({"receipt_ids": ["different-receipt"]}), operation),
        )
    else:
        binding = job.inputs[0]
        payload = copy.deepcopy(ledger.store.get(binding.kind, binding.id)["payload"])
        payload["engine"] = "revised fictional transcript"
        ledger.put(binding.kind, payload, binding.revision)
    with pytest.raises(ValueError):
        recover_jev_operation(
            ledger, operation, receipt, actor="local-owner", reason="Inspect rejection"
        )
    assert not ledger.store.all("decision_run") and not calls
    assert "decision" not in (journal.get(operation)["usage"] or {})


def test_owner_authorizes_one_new_attempt_not_unbounded_replay(remote_case, monkeypatch):
    ledger, settings, job, calls = remote_case
    journal, operation, key, _receipt = historical_operation(remote_case)
    original = journal.get(operation)
    worker = Worker(ledger, settings, handlers(), heartbeat=False)
    jid = worker.queue.submit(job)
    assert worker.run_once()["state"] == "blocked"
    grant = journal.authorize_retry(
        operation, actor="local-owner", reason="Approve one fictional new attempt"
    )
    assert not calls and grant["maximum_new_attempts"] == 1
    worker.queue.requeue(jid, reason="Owner approved one new provider attempt")
    # The one attempt is ambiguous: even another explicit requeue cannot spend a third time.
    real_client = jev.JevClient

    def client(*_args, **kwargs):
        class Unavailable:
            def __enter__(self):
                return self

            def __exit__(self, *_):
                pass

            def evaluate(self, *_args, **_kwargs):
                calls.append("mock timeout")
                raise httpx.ReadTimeout("fictional")

        return Unavailable()

    monkeypatch.setattr(jev, "JevClient", client)
    assert worker.run_once()["state"] == "blocked"
    worker.queue.requeue(jid, reason="Inspect only")
    assert worker.run_once()["state"] == "blocked"
    assert len(calls) == 1 and len(journal.list()) == 2
    assert journal.get(operation) == original  # Prior costs and history never overwritten.
    assert journal.authorizations()[0]["state"] == "consumed"
    assert journal.authorizations()[0]["actor"] == "local-owner"
    assert any(e["type"] == "provider.retry_authorization_consumed" for e in audit_events(ledger))
    assert real_client is not None and not journal.retry_authorized(key, "typesafe")


def test_authorized_new_attempt_can_succeed_after_reconciliation(remote_case):
    ledger, settings, job, calls = remote_case
    journal, operation, _key, _receipt = historical_operation(remote_case)
    journal.authorize_retry(operation, actor="local-owner", reason="One fresh mocked response")
    worker = Worker(ledger, settings, handlers(), heartbeat=False)
    worker.queue.submit(job)
    assert worker.run_once()["state"] == "succeeded"
    assert len(calls) == 1 and len(journal.list()) == 2
    assert journal.get(operation)["actual_micro_usd"] == 7


def test_authorization_is_single_use_across_competing_connections(remote_case):
    ledger, _settings, _job, calls = remote_case
    journal, operation, key, _receipt = historical_operation(remote_case)
    journal.authorize_retry(operation, actor="local-owner", reason="Concurrent fictional attempts")

    def reserve(name):
        store = Store(ledger.store.path)
        try:
            OperationJournal(store).begin(
                name, key, "typesafe", estimate_micro_usd=10, budget_micro_usd=100
            )
            return True
        except OperationBlocked:
            return False
        finally:
            store.close()

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(reserve, ["attempt-a", "attempt-b"])) == [False, True]
    assert len(journal.list()) == 2 and not calls
    assert sum(g["state"] == "consumed" for g in journal.authorizations()) == 1


@pytest.mark.parametrize(
    "condition", ["budget", "history", "unreconciled", "blank_actor", "blank_reason"]
)
def test_retry_authorization_fails_closed(remote_case, condition):
    ledger, _settings, _job, calls = remote_case
    journal, operation, key, _receipt = historical_operation(remote_case)
    if condition == "unreconciled":
        ledger.store.db.execute(
            "UPDATE provider_operations SET state='unknown' WHERE id=?", (operation,)
        )
    if condition in {"unreconciled", "blank_actor", "blank_reason"}:
        with pytest.raises((ValueError, OperationBlocked)):
            journal.authorize_retry(
                operation,
                actor=" " if condition == "blank_actor" else "local-owner",
                reason=" " if condition == "blank_reason" else "Fictional",
            )
        assert not journal.authorizations()
    else:
        journal.authorize_retry(operation, actor="local-owner", reason="Fictional single attempt")
        if condition == "history":
            journal.reconcile(operation, actual_micro_usd=8, evidence="Corrected billing")
        with pytest.raises(OperationBlocked):
            journal.begin(
                "new",
                key,
                "typesafe",
                estimate_micro_usd=10,
                budget_micro_usd=10 if condition == "budget" else 100,
            )
        assert journal.authorizations()[0]["state"] == "issued" and len(journal.list()) == 1
    assert not calls


def test_unsent_cancel_consumes_one_authorized_reservation(remote_case):
    _ledger, _settings, _job, calls = remote_case
    journal, operation, key, _receipt = historical_operation(remote_case)
    journal.authorize_retry(operation, actor="local-owner", reason="One reservation")
    journal.begin("retry", key, "typesafe", estimate_micro_usd=10, budget_micro_usd=100)
    journal.cancel_unsent("retry")
    with pytest.raises(OperationBlocked):
        journal.begin("retry-again", key, "typesafe", estimate_micro_usd=10, budget_micro_usd=100)
    assert journal.get("retry")["actual_micro_usd"] == 0 and not calls


def test_receipt_recovery_revokes_unused_retry_permission(remote_case):
    ledger, _settings, _job, calls = remote_case
    journal, operation, key, receipt = historical_operation(remote_case)
    journal.authorize_retry(operation, actor="local-owner", reason="Before finding raw receipt")
    recover_jev_operation(
        ledger, operation, receipt, actor="local-owner", reason="Found valid response"
    )
    assert not journal.retry_authorized(key, "typesafe")
    assert journal.authorizations()[0]["state"] == "revoked" and not calls


@pytest.mark.parametrize("model", ["jev-latest", "jev-preview", "jev-1.13.0"])
def test_worker_never_reuses_alias_or_expired_canonical_or_journal_result(
    remote_case, monkeypatch, model
):
    ledger, settings, job, calls = remote_case
    settings = settings.model_copy(update={"jev_model": model})
    job = job.model_copy(update={"config_sha256": settings.execution_hash()})
    worker = Worker(ledger, settings, handlers(), heartbeat=False)
    worker.queue.submit(job)
    # Fixture always resolves to the pinned model, including requests through an alias.
    assert worker.run_once()["state"] == "succeeded"
    if model == "jev-1.13.0":
        future = now() + timedelta(days=2)
        monkeypatch.setattr(jev, "now", lambda: future)
    updated = settings.model_copy(update={"remote_budget_micro_usd": 200})
    worker.queue.submit(job.model_copy(update={"config_sha256": updated.execution_hash()}))
    result = Worker(ledger, updated, handlers(), heartbeat=False).run_once()
    assert result["state"] == "blocked"  # Never a cache hit AND never implicit re-spending.
    assert len(calls) == 1
    assert len(ledger.store.all("decision_run")) == 1


@pytest.mark.parametrize("model", ["jev-latest", "jev-preview", "jev-1.13.0"])
def test_direct_path_uses_identical_cache_policy(remote_case, monkeypatch, model):
    ledger, settings, job, calls = remote_case
    config = jev.JevConfig(model=model, max_attempts=1, cache_seconds=1)
    with jev.JevClient("synthetic", config=config) as client:
        first = jev.run_decision(ledger, job.parameters["request"], client)
        if model == "jev-1.13.0":
            future = now() + timedelta(seconds=2)
            monkeypatch.setattr(jev, "now", lambda: future)
        second = jev.run_decision(ledger, job.parameters["request"], client)
    assert not first["cache_hit"] and not second["cache_hit"] and len(calls) == 2


def test_pinned_current_direct_cache_preserves_identity(remote_case):
    ledger, settings, job, calls = remote_case
    with jev.JevClient("synthetic", config=jev.JevConfig(max_attempts=1)) as client:
        first = jev.run_decision(ledger, job.parameters["request"], client)
        second = jev.run_decision(ledger, job.parameters["request"], client)
    assert (
        second["cache_hit"] and first["record"]["id"] == second["record"]["id"] and len(calls) == 1
    )


@pytest.mark.parametrize(
    "offset,ttl,expected", [(-1, 10, True), (-10, 10, False), (1, 10, False), (0, 0, False)]
)
def test_shared_cache_boundary(offset, ttl, expected):
    current = now()
    payload = {
        "status": "available",
        "model_requested": "jev-1.13.0",
        "captured_at": (current + timedelta(seconds=offset)).isoformat(),
    }
    assert jev.cache_eligible(payload, jev.JevConfig(cache_seconds=ttl), at=current) is expected


def test_local_cli_owner_recovery_actions(remote_case):
    ledger, settings, job, calls = remote_case
    journal, operation, key, receipt = historical_operation(remote_case)
    parser = argparse.ArgumentParser()
    add_commands(parser.add_subparsers(dest="command", required=True))
    args = parser.parse_args(
        ["authorize-operation-retry", operation, "--reason", "Fictional CLI approval"]
    )
    approval = execute(args, settings)
    assert approval["maximum_new_attempts"] == 1 and not calls
    args = parser.parse_args(
        [
            "revoke-operation-retry",
            approval["authorization_id"],
            "--reason",
            "Prefer receipt recovery",
        ]
    )
    execute(args, settings)
    assert not journal.retry_authorized(key, "typesafe")
    args = parser.parse_args(
        [
            "recover-operation-decision",
            operation,
            "--receipt-id",
            receipt,
            "--reason",
            "Reviewed fictional receipt",
        ]
    )
    assert execute(args, settings)["revision"] == 1
    assert execute(args, settings)["revision"] == 1
    assert not calls
    event = [
        e for e in audit_events(ledger) if e["type"] == "provider.decision_recovered_by_owner"
    ][-1]
    assert event["actor"] == "local-owner" and event["reason"] == args.reason
    bad = parser.parse_args(["authorize-operation-retry", operation, "--reason", " "])
    with pytest.raises(ValueError):
        execute(bad, settings)
    with pytest.raises(SystemExit):
        parser.parse_args(["authorize-operation-retry", operation])


def test_migration_four_preserves_prior_operation_and_audit_rows(ledger):
    journal = OperationJournal(ledger.store)
    journal.begin("historical", "a" * 64, "mock", estimate_micro_usd=1, budget_micro_usd=10)
    journal.unknown("historical")
    before = list(map(tuple, ledger.store.db.execute("SELECT * FROM provider_operations")))
    audit = list(map(tuple, ledger.store.db.execute("SELECT * FROM audit")))
    ledger.store.db.execute("DROP TABLE provider_retry_authorizations")
    ledger.store.db.execute("DELETE FROM foundation_migrations WHERE version=4")
    with pytest.raises(MigrationError):
        Store(ledger.store.path)
    assert migrate(ledger.store.path)["applied"] == [4]
    assert list(map(tuple, ledger.store.db.execute("SELECT * FROM provider_operations"))) == before
    assert list(map(tuple, ledger.store.db.execute("SELECT * FROM audit"))) == audit


def test_accounted_direct_call_cannot_hide_extra_transport_retries(remote_case):
    ledger, _settings, job, calls = remote_case
    with jev.JevClient("synthetic", config=jev.JevConfig(max_attempts=3)) as client:
        client.operation_policy = (10, 100)
        with pytest.raises(ValueError, match="one transport attempt"):
            jev.run_decision(ledger, job.parameters["request"], client)
    assert not calls and not OperationJournal(ledger.store).list()


def test_authorization_revocation_is_explicit_and_audited(remote_case):
    ledger, _settings, _job, calls = remote_case
    journal, operation, key, _receipt = historical_operation(remote_case)
    authorization = journal.authorize_retry(
        operation, actor="local-owner", reason="Initial permission"
    )
    with pytest.raises(OperationBlocked):
        journal.authorize_retry(operation, actor="local-owner", reason="Do not stack permits")
    journal.revoke_retry(
        authorization["authorization_id"], actor="local-owner", reason="Permission withdrawn"
    )
    with pytest.raises(OperationBlocked):
        journal.begin("fresh-attempt", key, "typesafe", estimate_micro_usd=10, budget_micro_usd=100)
    assert journal.authorizations()[0]["state"] == "revoked" and not calls
    assert audit_events(ledger)[-1]["type"] == "provider.retry_authorization_revoked"


def test_fourth_migration_failure_preserves_v3_data(ledger):
    journal = OperationJournal(ledger.store)
    journal.begin("historical", "a" * 64, "mock", estimate_micro_usd=1, budget_micro_usd=10)
    ledger.store.db.execute("DROP TABLE provider_retry_authorizations")
    ledger.store.db.execute("DELETE FROM foundation_migrations WHERE version=4")
    before = list(map(tuple, ledger.store.db.execute("SELECT * FROM provider_operations")))

    def fail(version):
        if version == 4:
            raise RuntimeError("Injected pre-migration failure")

    with pytest.raises(RuntimeError):
        migrate(ledger.store.path, before_version=fail)
    assert list(map(tuple, ledger.store.db.execute("SELECT * FROM provider_operations"))) == before
    assert (
        ledger.store.db.execute("SELECT max(version) FROM foundation_migrations").fetchone()[0] == 3
    )
    assert migrate(ledger.store.path)["applied"] == [4]


def test_explicit_authorization_refreshes_instead_of_reusing_current_result(remote_case):
    ledger, settings, job, calls = remote_case
    worker = Worker(ledger, settings, handlers(), heartbeat=False)
    worker.queue.submit(job)
    assert worker.run_once()["state"] == "succeeded"
    journal = OperationJournal(ledger.store)
    operation = journal.list()[0]["id"]
    journal.authorize_retry(
        operation, actor="local-owner", reason="Explicitly request one fresh decision"
    )
    next_settings = settings.model_copy(update={"remote_budget_micro_usd": 200})
    worker.queue.submit(job.model_copy(update={"config_sha256": next_settings.execution_hash()}))
    result = Worker(ledger, next_settings, handlers(), heartbeat=False).run_once()
    assert result["state"] == "succeeded" and not result["result"]["cache_hit"]
    assert len(calls) == 2 and len(journal.list()) == 2
    assert len(ledger.store.all("decision_run")) == 2
