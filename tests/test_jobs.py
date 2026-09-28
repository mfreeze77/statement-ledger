import pytest

from statement_ledger.jobs import JobQueue


def test_idempotent_enqueue(tmp_path):
    q = JobQueue(tmp_path / "jobs.db")
    try:
        a = q.enqueue({"kind": "metadata", "query": "Example"})
        b = q.enqueue({"kind": "metadata", "query": "Example"})
        assert a == b
    finally:
        q.close()


def test_different_payload_same_key_rejected(tmp_path):
    q = JobQueue(tmp_path / "jobs.db")
    try:
        q.enqueue({"a": 1}, key="key")
        with pytest.raises(ValueError):
            q.enqueue({"a": 2}, key="key")
    finally:
        q.close()


def test_lease_reclaim_and_stale_completion(tmp_path):
    q = JobQueue(tmp_path / "jobs.db")
    try:
        jid = q.enqueue({"kind": "test"})
        a = q.claim(clock=9999999999, lease_seconds=10)
        assert q.claim(clock=9999999999) is None
        b = q.claim(clock=10000000010, lease_seconds=10)
        assert b["lease_token"] != a["lease_token"]
        with pytest.raises(ValueError):
            q.finish(jid, a["lease_token"], {}, clock=10000000011)
        q.finish(jid, b["lease_token"], {"ok": True}, clock=10000000011)
        assert q.list()[0]["state"] == "succeeded"
    finally:
        q.close()


def test_exhausted_jobs_stop(tmp_path):
    q = JobQueue(tmp_path / "jobs.db")
    try:
        q.enqueue({"a": 1}, max_attempts=1)
        a = q.claim(clock=9999999999, lease_seconds=1)
        q.fail(a["id"], a["lease_token"], "transient", clock=9999999999)
        assert q.claim(clock=10000000010) is None
        assert q.list()[0]["state"] == "failed"
    finally:
        q.close()


def test_expired_lease_cannot_finish(tmp_path):
    q = JobQueue(tmp_path / "jobs.db")
    try:
        q.enqueue({"a": 1})
        a = q.claim(clock=9999999999, lease_seconds=1)
        with pytest.raises(ValueError):
            q.finish(a["id"], a["lease_token"], {}, clock=10000000001)
    finally:
        q.close()
