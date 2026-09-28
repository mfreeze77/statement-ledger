"""Foundation regression tests: no provider calls, secrets, weights, or real people."""

from __future__ import annotations

import io
import json
import logging
import sqlite3
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from statement_ledger.application.acceleration_demo import seed_acceleration
from statement_ledger.application.handlers import handlers
from statement_ledger.application.ledger import validators
from statement_ledger.contracts.models import KINDS
from statement_ledger.contracts.runtime import ArtifactInput, Binding, JobRequest
from statement_ledger.core.validation import ReadLedger, ValidatorRegistry
from statement_ledger.infrastructure.artifacts import LocalArtifactStore
from statement_ledger.infrastructure.backup import backup, restore
from statement_ledger.infrastructure.logging import SafeJSONFormatter
from statement_ledger.infrastructure.migrations import MigrationError, migrate, wal_is_fixed
from statement_ledger.infrastructure.operations import OperationBlocked, OperationJournal
from statement_ledger.infrastructure.queue import LeaseLost, RuntimeQueue
from statement_ledger.infrastructure.secrets import LocalSecrets
from statement_ledger.infrastructure.settings import Settings, load_settings, read_dotenv
from statement_ledger.infrastructure.sqlite_store import Store
from statement_ledger.infrastructure.worker import (
    Handler,
    PreparedResult,
    RecordWrite,
    Worker,
)


def settings_for(ledger, tmp_path):
    return Settings(data_root=tmp_path / "workspace", db_path=Path(ledger.store.path))


def request_for(ledger, settings, handler, parameters, inputs=(), artifacts=None, **kwargs):
    for artifact in (artifacts or {}).values():
        with ledger.store.transaction():
            ledger.store.db.execute(
                "INSERT OR IGNORE INTO artifact_refs VALUES(?,?,?,?)",
                (artifact.key, artifact.sha256, artifact.size, time.time()),
            )
    bindings = []
    for kind, record_id in inputs:
        row = ledger.store.get(kind, record_id)
        bindings.append(
            Binding(kind=kind, id=record_id, revision=row["revision"], record_hash=row["hash"])
        )
    return JobRequest(
        handler=handler,
        parameters=parameters,
        inputs=bindings,
        artifacts=artifacts or {},
        config_sha256=settings.execution_hash(),
        **kwargs,
    )


def test_settings_precedence_and_paths(tmp_path, monkeypatch):
    config = tmp_path / "config.toml"
    config.write_text('[statement_ledger]\nport=8000\ndata_root="records"\n')
    dotenv = tmp_path / ".env"
    dotenv.write_text('SL_PORT=8001\nSL_LOG_LEVEL="WARNING"\n')
    settings = load_settings(
        config_file=config, env_file=dotenv, environ={"SL_PORT": "8002"}, overrides={"port": 8003}
    )
    assert settings.port == 8003 and settings.log_level == "WARNING"
    assert settings.data_root == tmp_path / "records"
    assert settings.database == tmp_path / "records/db/ledger.sqlite3"


def test_settings_disabled_provider_needs_no_credentials():
    assert load_settings(environ={}).jev_enabled is False
    assert LocalSecrets(environ={}).resolve("TYPESAFE_API_KEY", required=False) is None


@pytest.mark.parametrize(
    "env", [{"SL_ENABEL_JEV": "1"}, {"SL_PORT": "0"}, {"SL_WORKER_HEARTBEAT_SECONDS": "90"}]
)
def test_settings_reject_mistakes(env):
    with pytest.raises(ValueError):
        load_settings(environ=env)


def test_configuration_cannot_hold_a_secret(tmp_path):
    file = tmp_path / "bad.toml"
    file.write_text('[statement_ledger]\nsecret_api_token="do-not-print"\n')
    with pytest.raises(ValueError):
        load_settings(config_file=file, environ={})


def test_secret_alias_and_file_conflict(tmp_path):
    (tmp_path / "SL_SECRET_TYPESAFE_API_KEY").write_text("file-value\n")
    assert (
        LocalSecrets(
            environ={"TYPESAFE_API_KEY": "same", "SL_SECRET_TYPESAFE_API_KEY": "same"}
        ).value("TYPESAFE_API_KEY")
        == "same"
    )
    with pytest.raises(ValueError, match="Conflicting"):
        LocalSecrets(environ={"TYPESAFE_API_KEY": "environment-value"}, directory=tmp_path).resolve(
            "TYPESAFE_API_KEY"
        )
    secret = LocalSecrets(environ={}, directory=tmp_path).resolve("TYPESAFE_API_KEY")
    assert "file-value" not in str(secret)


def test_dotenv_does_not_execute_or_interpolate(tmp_path):
    path = tmp_path / ".env"
    path.write_text("KEY='$(touch bad)'\nOTHER=${KEY}\n")
    assert read_dotenv(path) == {"KEY": "$(touch bad)", "OTHER": "${KEY}"}
    assert not (tmp_path / "bad").exists()


def test_artifacts_immutable_bounded_and_verified(tmp_path):
    store = LocalArtifactStore(tmp_path)
    first = store.put_bytes(b"original source")
    assert store.put_bytes(b"original source") == first
    store.verify(first)
    with pytest.raises(ValueError):
        store.put(io.BytesIO(b"abcdef"), max_bytes=3)
    assert not list((tmp_path / ".staging").iterdir())
    with store.materialize(first, suffix=".wav") as path:
        assert path.read_bytes() == b"original source"
    assert not path.exists()
    (tmp_path / first.key).write_bytes(b"tampered")
    with pytest.raises(ValueError, match="integrity"):
        store.verify(first)


@pytest.mark.parametrize(
    "key", ["../outside", "/tmp/file", "sha256/aa/" + "b" * 64, "sha256/../" + "a" * 64]
)
def test_artifact_keys_cannot_escape(tmp_path, key):
    store = LocalArtifactStore(tmp_path)
    with pytest.raises(ValueError):
        store.open(key)


def test_artifact_symlink_rejected(tmp_path):
    store = LocalArtifactStore(tmp_path / "artifacts")
    (tmp_path / "outside").mkdir()
    (store.root / "sha256").symlink_to(tmp_path / "outside", target_is_directory=True)
    with pytest.raises(ValueError):
        store.put_bytes(b"source")
    assert not list((tmp_path / "outside").iterdir())


def test_runtime_never_implicitly_creates_or_migrates(tmp_path):
    path = tmp_path / "not-created.sqlite3"
    with pytest.raises(MigrationError):
        Store(path)
    assert not path.exists()
    migrate(path)
    store = Store(path)
    assert store.db.execute("PRAGMA journal_mode").fetchone()[0] == "delete"
    store.close()


def test_migration_rollback_and_retry(tmp_path):
    path = tmp_path / "migration.sqlite3"

    def fail(version):
        if version == 3:
            raise RuntimeError("injected")

    with pytest.raises(RuntimeError, match="injected"):
        migrate(path, before_version=fail)
    with sqlite3.connect(path) as database:
        assert not database.execute(
            "SELECT name FROM sqlite_master WHERE name='revisions'"
        ).fetchone()
    assert migrate(path)["applied"] == [1, 2, 3]
    assert migrate(path)["applied"] == []


def test_concurrent_migrations(tmp_path):
    path = tmp_path / "race.sqlite3"
    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(lambda _: migrate(path), range(2)))
    assert sorted(len(result["applied"]) for result in results) == [0, 3]


def test_unknown_migration_checksum_fails_closed(tmp_path):
    path = tmp_path / "checksum.sqlite3"
    migrate(path)
    with sqlite3.connect(path) as database:
        database.execute("UPDATE foundation_migrations SET sha256='tampered' WHERE version=2")
    with pytest.raises(MigrationError):
        migrate(path)
    with pytest.raises(MigrationError):
        Store(path)


def test_future_schema_is_not_downgraded(tmp_path):
    path = tmp_path / "future.sqlite3"
    migrate(path)
    with sqlite3.connect(path) as database:
        database.execute(
            "INSERT INTO foundation_migrations VALUES(99,'future.sql','unknown','future')"
        )
    with pytest.raises(MigrationError):
        migrate(path)


def test_existing_records_and_audit_survive_adoption(seeded):
    old = seeded.store.export()
    path = seeded.store.path
    seeded.store.db.execute("DROP TABLE foundation_migrations")
    # Drop only empty foundation runtime tables to reproduce a v0.2 layout.
    for table in (
        "job_artifacts",
        "artifact_refs",
        "work_attempts",
        "work_jobs",
        "provider_operations",
    ):
        seeded.store.db.execute("DROP TABLE " + table)
    migrate(path)
    assert seeded.store.export() == old
    assert seeded.store.verify_records()["valid"] and seeded.store.verify_audit()["valid"]


def test_legacy_jobs_are_not_abandoned(tmp_path):
    from statement_ledger.jobs import JobQueue

    legacy = tmp_path / "old-jobs.db"
    queue = JobQueue(legacy)
    queue.enqueue({"operator_task": "pending"})
    queue.close()
    with pytest.raises(MigrationError, match="separate legacy"):
        migrate(tmp_path / "new.sqlite3", legacy_jobs_path=legacy)


@pytest.mark.parametrize(
    "version, expected",
    [
        ((3, 46, 1), False),
        ((3, 51, 2), False),
        ((3, 51, 3), True),
        ((3, 44, 6), True),
        ((3, 50, 7), True),
    ],
)
def test_sqlite_wal_gate(version, expected):
    assert wal_is_fixed(version) is expected


def test_validator_registry_missing_duplicate_and_sealed():
    registry = ValidatorRegistry()
    with pytest.raises(ValueError):
        registry.check(KINDS)
    registry.register("person", lambda *_: None)
    with pytest.raises(ValueError):
        registry.register("person", lambda *_: None)
    complete = validators()
    complete.check(KINDS)
    with pytest.raises(ValueError):
        complete.register("new-kind", lambda *_: None)


def test_validation_context_has_no_write_or_sql(ledger):
    view = ReadLedger(ledger)
    assert (
        not hasattr(view, "put")
        and not hasattr(view.store, "db")
        and not hasattr(view.store, "write")
    )


def test_nested_transaction_rolls_back_canonical_effects(ledger):
    with pytest.raises(RuntimeError):
        with ledger.store.transaction():
            ledger.put("person", {"id": "will-rollback", "display_name": "Synthetic"})
            raise RuntimeError("crash")
    assert ledger.store.counts() == {}
    assert ledger.store.verify_audit()["checked"] == 0


def test_outbox_dispatch_is_atomic_and_idempotent(seeded, tmp_path):
    settings = settings_for(seeded, tmp_path)
    request = request_for(seeded, settings, "media.clip", {})
    queue = RuntimeQueue(seeded.store)
    identity = queue.submit(request)
    queue.submit(request)
    while queue.dispatch()["dispatched"]:
        pass
    assert len(queue.list()) == 1 and queue.get(identity)["state"] == "pending"
    assert queue.get(identity)["payload"]["run_id"] == request.run_id


def test_heartbeat_and_expired_fence(ledger, tmp_path):
    queue = RuntimeQueue(ledger.store)
    settings = settings_for(ledger, tmp_path)
    identity = queue.submit(request_for(ledger, settings, "media.clip", {}))
    queue.dispatch()
    clock = time.time() + 1
    first = queue.claim(lease_seconds=2, clock=clock)
    queue.heartbeat(identity, first["lease_token"], lease_seconds=5, clock=clock + 1)
    assert queue.claim(clock=clock + 3) is None
    second = queue.claim(clock=clock + 7)
    with ledger.store.transaction(), pytest.raises(LeaseLost):
        queue.finish(identity, first["lease_token"], {}, clock=clock + 8)
    with ledger.store.transaction():
        queue.finish(identity, second["lease_token"], {}, clock=clock + 8)
    assert queue.get(identity)["state"] == "succeeded"


def test_cancellation_fences_results(ledger, tmp_path):
    queue = RuntimeQueue(ledger.store)
    identity = queue.submit(request_for(ledger, settings_for(ledger, tmp_path), "media.clip", {}))
    queue.dispatch()
    job = queue.claim()
    queue.cancel(identity)
    with ledger.store.transaction(), pytest.raises(LeaseLost):
        queue.finish(identity, job["lease_token"], {})
    assert queue.get(identity)["state"] == "cancelled"


def test_transcript_job_runs_and_deduplicates(seeded, tmp_path):
    settings = settings_for(seeded, tmp_path)
    artifact = LocalArtifactStore(settings.artifacts).put_bytes(
        b"WEBVTT\n\n00:00:01.000 --> 00:00:02.000\nSynthetic imported caption.\n"
    )
    request = request_for(
        seeded,
        settings,
        "transcript.import",
        {"asset_id": "asset-original", "transcript_id": "queued-transcript", "format": "vtt"},
        [("asset", "asset-original")],
        {"transcript": ArtifactInput(**artifact.as_dict())},
    )
    queue = RuntimeQueue(seeded.store)
    identity = queue.submit(request)
    worker = Worker(seeded, settings, handlers(), heartbeat=False)
    assert worker.run_once()["state"] == "succeeded"
    assert seeded.store.get("transcript", "queued-transcript")["revision"] == 1
    queue.submit(request)
    assert worker.run_once() is None
    assert queue.get(identity)["result"]["identity_confirmed"] is False


def test_changed_source_during_work_cannot_commit(seeded, tmp_path):
    settings = settings_for(seeded, tmp_path)
    request = request_for(
        seeded, settings, "synthetic.stale", {}, [("transcript", "transcript-asset-original")]
    )

    def prepare(context, job):
        # Simulates a separate operator transaction while the worker is outside its write transaction.
        row = seeded.store.get("transcript", "transcript-asset-original")
        payload = row["payload"]
        payload["segments"][0]["text"] = "Corrected synthetic source"
        seeded.put("transcript", payload, row["revision"])
        assert seeded.store.get("review", "review-1")["stale"]
        return PreparedResult(
            records=[RecordWrite("person", {"id": "unsafe", "display_name": "Must not commit"})]
        )

    registered = {
        request.handler: Handler(
            request.handler, 1, "cpu", lambda *_: None, prepare, frozenset({"person"})
        )
    }
    RuntimeQueue(seeded.store).submit(request)
    result = Worker(seeded, settings, registered, heartbeat=False).run_once()
    assert result["state"] == "failed" and result["error_code"] == "stale_input"
    assert "unsafe" not in [row["id"] for row in seeded.store.all("person")]


def test_handler_cannot_write_before_the_fence(seeded, tmp_path):
    settings = settings_for(seeded, tmp_path)
    request = request_for(seeded, settings, "synthetic.illegal", {})

    def prepare(context, job):
        context.ledger.put("person", {"id": "unsafe", "display_name": "Must not commit"})
        return PreparedResult()

    registered = {
        request.handler: Handler(
            request.handler, 1, "cpu", lambda *_: None, prepare, frozenset({"person"})
        )
    }
    RuntimeQueue(seeded.store).submit(request)
    assert Worker(seeded, settings, registered, heartbeat=False).run_once()["state"] == "failed"
    assert "unsafe" not in [row["id"] for row in seeded.store.all("person")]


def test_localization_through_worker(ledger, tmp_path):
    seed_acceleration(ledger)
    settings = settings_for(ledger, tmp_path)
    request = request_for(
        ledger,
        settings,
        "speech.localize",
        {"profile_id": "profile-demo", "transcript_id": "style-heldout-transcript"},
        [("speaker_profile", "profile-demo"), ("transcript", "style-heldout-transcript")],
    )
    RuntimeQueue(ledger.store).submit(request)
    result = Worker(ledger, settings, handlers(), heartbeat=False).run_once()
    assert result["state"] == "succeeded"
    row = ledger.store.get("localization_run", result["result"]["records"][0]["id"])
    assert row["payload"]["selected_audio_ms"] == 600000


def test_provider_budget_and_unknown_outcome(ledger):
    journal = OperationJournal(ledger.store)
    with pytest.raises(OperationBlocked):
        journal.begin("a", "a" * 64, "mock", estimate_micro_usd=10, budget_micro_usd=0)
    journal.begin("a", "a" * 64, "mock", estimate_micro_usd=10, budget_micro_usd=10)
    journal.unknown("a")
    with pytest.raises(OperationBlocked):
        journal.begin("a", "a" * 64, "mock", estimate_micro_usd=10, budget_micro_usd=100)
    with pytest.raises(OperationBlocked):
        journal.begin("b", "b" * 64, "mock", estimate_micro_usd=1, budget_micro_usd=10)
    assert journal.list()[0]["cost_status"] == "unknown"
    journal.reconcile("a", actual_micro_usd=7, evidence="Synthetic provider receipt")
    assert journal.list()[0]["actual_micro_usd"] == 7


def test_structured_logs_do_not_emit_messages_or_provider_data():
    record = logging.LogRecord(
        "ledger",
        logging.ERROR,
        "",
        0,
        "secret-value https://example.com?key=secret-value",
        (),
        None,
    )
    record.event_code = "work.failed"
    record.safe_fields = {
        "job_id": "job-example",
        "error_code": "provider_unavailable",
        "authorization": "secret-value",
        "response_body": "sensitive transcript",
    }
    encoded = SafeJSONFormatter().format(record)
    assert "secret-value" not in encoded and "sensitive transcript" not in encoded
    assert json.loads(encoded)["job_id"] == "job-example"


def test_workspace_backup_restore_and_tamper(seeded, tmp_path):
    settings = settings_for(seeded, tmp_path)
    artifact = LocalArtifactStore(settings.artifacts).put_bytes(b"Retained synthetic source")
    with seeded.store.transaction():
        seeded.store.db.execute(
            "INSERT INTO artifact_refs VALUES(?,?,?,?)",
            (artifact.key, artifact.sha256, artifact.size, time.time()),
        )
    before = seeded.store.export()
    directory = tmp_path / "backup"
    manifest = backup(settings, directory)
    assert manifest["scope"] == "canonical_database_and_registered_artifacts"
    target = tmp_path / "restored"
    assert restore(directory, target)["records_and_audit_verified"]
    restored = Store(target / "db/ledger.sqlite3")
    assert restored.export() == before
    restored.close()
    with pytest.raises(ValueError, match="must not exist"):
        restore(directory, target)
    (directory / "artifacts" / artifact.key).write_bytes(b"tampered")
    with pytest.raises(ValueError):
        restore(directory, tmp_path / "bad-restore")
