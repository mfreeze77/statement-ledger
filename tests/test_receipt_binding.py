"""SL-301: recovery must use the receipt's originating operation, never a clock window.

Only fictional source data, local SQLite, and mocked transports are used here.
"""

from __future__ import annotations

import copy
import json
from datetime import timedelta

import pytest
import test_review_jobs as review_fixtures

from statement_ledger.application.handlers import handlers
from statement_ledger.application.operation_recovery import recover_jev_operation
from statement_ledger.core.util import digest
from statement_ledger.infrastructure.operations import OperationBlocked, OperationJournal
from statement_ledger.infrastructure.providers import jev
from statement_ledger.infrastructure.providers.jev import JevClient as OriginalJevClient
from statement_ledger.infrastructure.worker import Worker

remote_case = review_fixtures.remote_case


def snapshot(ledger):
    """Read persisted effects, including all audit columns, before a refused action."""
    return {
        table: list(map(tuple, ledger.store.db.execute(f"SELECT * FROM {table} ORDER BY rowid")))
        for table in ("provider_operations", "provider_retry_authorizations", "audit", "revisions")
    }


def request_metadata(case):
    _ledger, settings, job, _calls = case
    return {
        **copy.deepcopy(job.parameters["request"]),
        "endpoint": jev.ENDPOINT,
        "model": settings.jev_model,
        "validator": jev.VALIDATOR_VERSION,
    }


def own_receipt(case, *, recorded_operation="attempt-A"):
    ledger, settings, _job, _calls = case
    metadata = request_metadata(case)
    key = digest(metadata)
    journal = OperationJournal(ledger.store)
    journal.begin("attempt-A", key, "typesafe", estimate_micro_usd=10, budget_micro_usd=100)
    body = json.dumps(
        {
            "model": settings.jev_model,
            "answers": {"q": {"type": "noul", "noul": 0.7}},
            "usage": {"input_tokens": 8, "output_tokens": 1},
        }
    ).encode()
    if recorded_operation == "attempt-A":
        receipt = journal.capture_receipt("attempt-A", key, 1, 200, body, False, metadata)
    else:
        # Legacy/unbound capture or deliberately malformed provenance in a hard negative.
        receipt = ledger.store.capture_provider_response(key, 1, 200, body, False, metadata)
        if recorded_operation is not None:
            ledger.store.audit(
                {
                    "type": "provider.receipt_bound",
                    "receipt_id": receipt,
                    "operation_id": recorded_operation,
                    "request_hash": key,
                }
            )
    journal.unknown("attempt-A")
    journal.reconcile("attempt-A", actual_micro_usd=7, evidence="Fictional billing confirmation")
    return journal, key, receipt


@pytest.mark.parametrize("entrypoint", ["worker", "direct"])
@pytest.mark.parametrize("outcome", ["success", "invalid_body", "timeout"])
def test_capture_persists_operation_binding_before_response_validation(
    remote_case, monkeypatch, entrypoint, outcome
):
    ledger, _settings, job, calls = remote_case
    if outcome != "success":
        import httpx

        # Keep the original class imported at collection time, before the fixture
        # patches the constructor. No nested mock transports or real network.

        def respond(request):
            calls.append(request)
            if outcome == "timeout":
                raise httpx.ReadTimeout("Synthetic read timeout", request=request)
            return httpx.Response(200, content=b"not valid JSON")

        monkeypatch.setattr(
            jev,
            "JevClient",
            lambda key, **kw: OriginalJevClient(key, transport=httpx.MockTransport(respond), **kw),
        )
    if entrypoint == "worker":
        worker = Worker(ledger, remote_case[1], handlers(), heartbeat=False)
        worker.queue.submit(job)
        result = worker.run_once()
        assert result["state"] == ("succeeded" if outcome == "success" else "blocked")
    else:
        with jev.JevClient("synthetic", config=jev.JevConfig(max_attempts=1)) as client:
            client.operation_policy = (10, 100)
            result = jev.run_decision(ledger, job.parameters["request"], client)
            assert result["record"]["payload"]["status"] == (
                "available" if outcome == "success" else "unavailable"
            )
    operation = OperationJournal(ledger.store).list()[0]
    ids = [row[0] for row in ledger.store.db.execute("SELECT id FROM provider_receipts")]
    assert len(calls) == len(ids) == 1
    receipt = ledger.store.provider_receipt(ids[0])
    metadata = dict(receipt["request_metadata"])
    bindings = [
        json.loads(row[0])
        for row in ledger.store.db.execute(
            "SELECT event FROM audit WHERE json_extract(event,'$.type')='provider.receipt_bound'"
        )
    ]
    assert len(bindings) == 1 and bindings[0]["operation_id"] == operation["id"]
    assert bindings[0]["receipt_id"] == ids[0]
    OperationJournal(ledger.store).require_receipt_binding(operation["id"], ids[0])
    assert digest(metadata) == operation["request_hash"] == receipt["request_hash"]
    assert "operation_id" not in json.loads(calls[0].content)
    assert operation["state"] == ("completed" if outcome == "success" else "unknown")
    assert ledger.store.verify_audit()["valid"]


@pytest.mark.parametrize("extra_action", ["none", "authorize", "authorize_then_revoke"])
def test_attempt_b_receipt_cannot_be_recovered_for_reconciled_attempt_a(
    remote_case, monkeypatch, extra_action
):
    ledger, settings, job, calls = remote_case
    journal = OperationJournal(ledger.store)
    key = digest(request_metadata(remote_case))
    journal.begin("attempt-A", key, "typesafe", estimate_micro_usd=10, budget_micro_usd=100)
    journal.unknown("attempt-A")  # No receipt ids exist on the timed-out operation.
    journal.reconcile("attempt-A", actual_micro_usd=7, evidence="Fictional A billing")
    first = journal.get("attempt-A")
    journal.authorize_retry("attempt-A", actor="local-owner", reason="One fictional retry")

    def interrupted_completion(*_args, **_kwargs):
        raise RuntimeError("Synthetic interruption after capture, before completion")

    worker = Worker(ledger, settings, handlers(), heartbeat=False)
    worker.queue.submit(job)
    with monkeypatch.context() as patch:
        patch.setattr(OperationJournal, "complete", interrupted_completion)
        assert worker.run_once()["state"] == "blocked"
    second = next(op for op in journal.list() if op["id"] != "attempt-A")
    assert second["state"] == "unknown" and second["usage"] is None
    receipt_id = ledger.store.db.execute("SELECT id FROM provider_receipts").fetchone()[0]
    receipt = ledger.store.provider_receipt(receipt_id)
    assert receipt["request_hash"] == first["request_hash"]
    journal.reconcile(second["id"], actual_micro_usd=8, evidence="Fictional B billing")
    if extra_action != "none":
        grant = journal.authorize_retry(
            "attempt-A", actor="local-owner", reason="One additional fictional reservation"
        )
        if extra_action == "authorize_then_revoke":
            journal.revoke_retry(grant["authorization_id"], actor="local-owner", reason="Withdraw")
    before = snapshot(ledger)
    with pytest.raises(OperationBlocked):
        journal.reconcile("attempt-A", actual_micro_usd=7, evidence="Cannot widen A's interval")
    assert snapshot(ledger) == before
    with pytest.raises(ValueError, match="operation"):
        recover_jev_operation(
            ledger, "attempt-A", receipt_id, actor="local-owner", reason="Try unrelated B receipt"
        )
    assert snapshot(ledger) == before
    assert journal.get("attempt-A") == first
    assert not ledger.store.all("decision_run") and len(calls) == 1
    recovered = recover_jev_operation(
        ledger, second["id"], receipt_id, actor="local-owner", reason="B owns its receipt"
    )
    payload = ledger.store.get("decision_run", recovered["decision_id"])["payload"]
    assert payload["captured_at"].replace("Z", "+00:00") == receipt["captured_at"]
    assert payload["latency_ms"] is None and recovered["provider_calls"] == 0
    assert len(calls) == 1 and journal.get("attempt-A") == first
    assert ledger.store.verify_audit()["valid"]


@pytest.mark.parametrize("recorded_operation", [None, "", "attempt-B", 1, ["attempt-A"]])
def test_unbound_or_different_operation_receipt_is_refused(remote_case, recorded_operation):
    ledger, _settings, _job, calls = remote_case
    journal, key, receipt = own_receipt(remote_case, recorded_operation=recorded_operation)
    # Matching request and an explicit usage list are NOT a substitute for capture binding.
    ledger.store.db.execute(
        "UPDATE provider_operations SET usage=? WHERE id='attempt-A'",
        (json.dumps({"receipt_ids": [receipt]}),),
    )
    assert ledger.store.provider_receipt(receipt)["request_hash"] == key
    before = snapshot(ledger)
    with pytest.raises(ValueError, match="operation"):
        recover_jev_operation(
            ledger, "attempt-A", receipt, actor="local-owner", reason="Inspect capture binding"
        )
    assert snapshot(ledger) == before and not calls
    assert "decision" not in journal.get("attempt-A")["usage"]


def test_own_receipt_uses_binding_not_mutable_operation_time_window(remote_case):
    from statement_ledger.contracts.models import now

    ledger, _settings, _job, calls = remote_case
    journal, _key, receipt_id = own_receipt(remote_case)
    # Simulate a wall-clock adjustment: capture falls outside the old operation interval.
    captured_at = (now() - timedelta(days=2)).isoformat()
    ledger.store.db.execute(
        "UPDATE provider_receipts SET captured_at=? WHERE id=?", (captured_at, receipt_id)
    )
    before_receipt = ledger.store.provider_receipt(receipt_id)
    journal.require_receipt_binding("attempt-A", receipt_id)
    result = recover_jev_operation(
        ledger, "attempt-A", receipt_id, actor="local-owner", reason="Own intact receipt"
    )
    payload = ledger.store.get("decision_run", result["decision_id"])["payload"]
    assert payload["captured_at"].replace("Z", "+00:00") == captured_at
    assert payload["latency_ms"] is None and not calls
    assert ledger.store.provider_receipt(receipt_id) == before_receipt
    assert journal.get("attempt-A")["actual_micro_usd"] == 7


@pytest.mark.parametrize("state", ["completed", "cancelled", "reconciled"])
def test_reconcile_terminal_operation_is_refused_without_changes(ledger, state):
    journal = OperationJournal(ledger.store)
    journal.begin("attempt-A", "a" * 64, "mock", estimate_micro_usd=10, budget_micro_usd=100)
    if state == "completed":
        journal.complete("attempt-A", {"receipt_ids": []}, actual_micro_usd=7)
    elif state == "cancelled":
        journal.cancel_unsent("attempt-A")
    else:
        journal.unknown("attempt-A")
        journal.reconcile("attempt-A", actual_micro_usd=7, evidence="Fictional billing")
    before = snapshot(ledger)
    operation = journal.get("attempt-A")
    with pytest.raises(OperationBlocked):
        journal.reconcile("attempt-A", actual_micro_usd=99, evidence="Second reconciliation")
    assert journal.get("attempt-A") == operation
    assert snapshot(ledger) == before and ledger.store.verify_audit()["valid"]


@pytest.mark.parametrize("state", ["started", "unknown"])
def test_reconcile_ambiguous_operation_still_succeeds(ledger, state):
    journal = OperationJournal(ledger.store)
    journal.begin("attempt-A", "a" * 64, "mock", estimate_micro_usd=10, budget_micro_usd=100)
    if state == "unknown":
        journal.unknown("attempt-A")
    journal.reconcile("attempt-A", actual_micro_usd=7, evidence="Fictional billing", actor="owner")
    operation = journal.get("attempt-A")
    assert operation["state"] == "completed" and operation["actual_micro_usd"] == 7
    audit = json.loads(
        ledger.store.db.execute("SELECT event FROM audit ORDER BY rowid DESC LIMIT 1").fetchone()[0]
    )
    assert audit["type"] == "provider.operation_reconciled" and audit["actor"] == "owner"


def test_zero_row_grant_consumption_rolls_back_reservation_and_audit(remote_case):
    ledger, _settings, _job, calls = remote_case
    journal, key, _receipt = own_receipt(remote_case)
    grant = journal.authorize_retry("attempt-A", actor="local-owner", reason="One retry")
    # A real SQLite trigger makes the guarded UPDATE affect zero rows. No mock cursor.
    ledger.store.db.execute("""
        CREATE TEMP TRIGGER refuse_permission_consumption
        BEFORE UPDATE OF state ON provider_retry_authorizations
        WHEN NEW.state='consumed'
        BEGIN SELECT RAISE(IGNORE); END
    """)
    before = snapshot(ledger)
    with pytest.raises(OperationBlocked, match="consum"):
        journal.begin("attempt-B", key, "typesafe", estimate_micro_usd=10, budget_micro_usd=100)
    assert snapshot(ledger) == before and not calls
    assert journal.authorizations()[0]["id"] == grant["authorization_id"]
    assert journal.authorizations()[0]["state"] == "issued"
    assert [op["id"] for op in journal.list()] == ["attempt-A"]


def test_capture_and_binding_are_atomic(remote_case, monkeypatch):
    ledger, _settings, _job, calls = remote_case
    metadata = request_metadata(remote_case)
    key = digest(metadata)
    journal = OperationJournal(ledger.store)
    journal.begin("attempt-A", key, "typesafe", estimate_micro_usd=10, budget_micro_usd=100)
    before = snapshot(ledger)
    audit = ledger.store.audit

    def fail_binding(event):
        if event["type"] == "provider.receipt_bound":
            raise RuntimeError("Synthetic binding persistence failure")
        return audit(event)

    monkeypatch.setattr(ledger.store, "audit", fail_binding)
    with pytest.raises(RuntimeError, match="binding persistence"):
        journal.capture_receipt("attempt-A", key, 1, 200, b"{}", False, metadata)
    assert ledger.store.db.execute("SELECT count(*) FROM provider_receipts").fetchone()[0] == 0
    assert snapshot(ledger) == before and not calls


def test_late_receipt_stays_bound_to_origin_not_current_retry(remote_case):
    ledger, _settings, _job, calls = remote_case
    journal, key, original = own_receipt(remote_case)
    journal.authorize_retry("attempt-A", actor="local-owner", reason="One approved retry")
    journal.begin("attempt-B", key, "typesafe", estimate_micro_usd=10, budget_micro_usd=100)
    first_receipt = ledger.store.provider_receipt(original)
    # A's callback was created with A's id. A later reservation for identical content
    # must not steal that delayed capture, even though B is now the active operation.
    late = journal.capture_receipt(
        "attempt-A", key, 1, 200, first_receipt["body"], False, first_receipt["request_metadata"]
    )
    journal.require_receipt_binding("attempt-A", late)
    with pytest.raises(ValueError, match="different provider operation"):
        journal.require_receipt_binding("attempt-B", late)
    assert journal.get("attempt-B")["state"] == "started"
    assert ledger.store.verify_audit()["valid"] and not calls


def test_multiple_operation_bindings_are_refused(remote_case):
    ledger, _settings, _job, calls = remote_case
    journal, key, receipt = own_receipt(remote_case)
    ledger.store.audit(
        {
            "type": "provider.receipt_bound",
            "receipt_id": receipt,
            "operation_id": "attempt-A",
            "request_hash": key,
        }
    )
    before = snapshot(ledger)
    with pytest.raises(ValueError, match="exactly one"):
        recover_jev_operation(
            ledger, "attempt-A", receipt, actor="local-owner", reason="Reject ambiguous binding"
        )
    assert snapshot(ledger) == before and not calls
    assert not ledger.store.all("decision_run")


@pytest.mark.parametrize("invalid", ["request_hash", "cancelled"])
def test_capture_refuses_mismatched_or_cancelled_operation(remote_case, invalid):
    ledger, _settings, _job, calls = remote_case
    metadata = request_metadata(remote_case)
    key = digest(metadata)
    journal = OperationJournal(ledger.store)
    journal.begin("attempt-A", key, "typesafe", estimate_micro_usd=10, budget_micro_usd=100)
    if invalid == "cancelled":
        journal.cancel_unsent("attempt-A")
    before = snapshot(ledger)
    with pytest.raises(OperationBlocked):
        journal.capture_receipt(
            "attempt-A",
            "wrong" if invalid == "request_hash" else key,
            1,
            200,
            b"{}",
            False,
            metadata,
        )
    assert snapshot(ledger) == before and not calls
    assert ledger.store.db.execute("SELECT count(*) FROM provider_receipts").fetchone()[0] == 0
