"""Migration, backup and portable-key regressions requested in PR #1 review."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path, PureWindowsPath
from types import SimpleNamespace

import pytest
from legacy_v02 import frozen_rows, legacy_types, populated_legacy

from statement_ledger.infrastructure import backup as backup_module
from statement_ledger.infrastructure import sqlite_store
from statement_ledger.infrastructure.artifacts import LocalArtifactStore
from statement_ledger.infrastructure.backup import backup, checksum, restore
from statement_ledger.infrastructure.migrations import CORE_COLUMNS, MigrationError, migrate
from statement_ledger.infrastructure.settings import Settings
from statement_ledger.infrastructure.sqlite_store import Store


@pytest.mark.parametrize("state", ["succeeded", "failed"])
def test_real_v02_wal_fts_jobs_and_exact_historical_rows_survive(tmp_path, state):
    path = tmp_path / "ledger.sqlite3"
    legacy = populated_legacy(path, job_state=state)
    assert legacy.db.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
    assert legacy.db.execute("SELECT version FROM schema_migrations").fetchone()[0] == 2
    assert legacy.db.execute("SELECT count(*) FROM claim_search").fetchone()[0] == 1
    before = frozen_rows(legacy.db)
    assert legacy.get("proposition", "fixture-claim")["stale"]
    legacy.close()
    assert migrate(path)["applied"] == [1, 2, 3, 4]
    current = Store(path)
    try:
        assert frozen_rows(current.db) == before
        assert current.verify_records()["valid"] and current.verify_audit()["valid"]
        assert current.verify_provider_receipts()["checked"] == 1
        assert current.get("person", "fixture-person")["revision"] == 2
    finally:
        current.close()


def test_real_v02_pending_in_ledger_job_blocks_without_changes(tmp_path):
    path = tmp_path / "ledger.sqlite3"
    legacy = populated_legacy(path, job_state="pending")
    before = frozen_rows(legacy.db)
    legacy.close()
    with pytest.raises(MigrationError, match="non-terminal"):
        migrate(path)
    with sqlite3.connect(path) as connection:
        assert frozen_rows(connection) == before
        assert not connection.execute(
            "SELECT 1 FROM sqlite_master WHERE name='foundation_migrations'"
        ).fetchone()


@pytest.mark.parametrize("state", ["succeeded", "failed", "cancelled"])
def test_finished_separate_legacy_jobs_preserved_not_blocking(tmp_path, state):
    _, OldQueue = legacy_types()
    sidecar = tmp_path / "jobs.sqlite3"
    queue = OldQueue(sidecar)
    jid = queue.enqueue({"task": "synthetic"})
    queue.db.execute("UPDATE jobs SET state=? WHERE id=?", (state, jid))
    before = tuple(queue.db.execute("SELECT * FROM jobs").fetchone())
    queue.close()
    migrate(tmp_path / "ledger.sqlite3", legacy_jobs_path=sidecar)
    with sqlite3.connect(sidecar) as connection:
        assert tuple(connection.execute("SELECT * FROM jobs").fetchone()) == before


def test_missing_all_core_tables_refused_at_open_and_restore(tmp_path):
    settings = Settings(data_root=tmp_path / "workspace")
    migrate(settings.database)
    settings.prepare_directories()
    source = tmp_path / "snapshot"
    backup(settings, source)
    database_path = source / "ledger.sqlite3"
    with sqlite3.connect(database_path) as database:
        for table in CORE_COLUMNS:
            database.execute('DROP TABLE "' + table + '"')
    manifest = json.loads((source / "manifest.json").read_text())
    manifest["database_sha256"] = checksum(database_path)
    (source / "manifest.json").write_text(json.dumps(manifest))
    with pytest.raises(MigrationError, match="required core"):
        Store(database_path)
    with pytest.raises(MigrationError, match="required core"):
        restore(source, tmp_path / "restored")
    assert not (tmp_path / "restored").exists()


def test_windows_orphan_keys_are_posix_not_backslashes(tmp_path):
    artifacts = LocalArtifactStore(tmp_path / "objects")
    artifact = artifacts.put_bytes(b"synthetic")
    actual_root = artifacts.root
    file = SimpleNamespace(
        relative_to=lambda _root: PureWindowsPath(artifact.key),
        is_file=lambda: True,
        is_symlink=lambda: False,
    )
    artifacts.root = SimpleNamespace(glob=lambda _: [file])
    assert artifacts.inspect_orphans({artifact.key}) == {
        "unreferenced": [],
        "missing": [],
        "staging": [],
    }
    artifacts.root = actual_root
    assert artifacts.inspect_orphans({artifact.key})["missing"] == []


def test_failed_backup_initialization_cleans_destination_and_can_retry(tmp_path):
    settings = Settings(data_root=tmp_path / "workspace")
    destination = tmp_path / "backup"
    with pytest.raises(MigrationError):
        backup(settings, destination)
    assert not destination.exists()
    migrate(settings.database)
    assert backup(settings, destination)["database_sha256"]


def test_failed_artifact_initialization_cleans_backup(tmp_path, monkeypatch):
    settings = Settings(data_root=tmp_path / "workspace")
    migrate(settings.database)
    destination = tmp_path / "backup"

    def broken(*args, **kwargs):
        raise OSError("synthetic constructor failure")

    monkeypatch.setattr(backup_module, "LocalArtifactStore", broken)
    with pytest.raises(OSError):
        backup(settings, destination)
    assert not destination.exists()


def test_restore_detects_corruption_in_copied_database(tmp_path, monkeypatch):
    settings = Settings(data_root=tmp_path / "workspace")
    migrate(settings.database)
    source, destination = tmp_path / "backup", tmp_path / "restored"
    backup(settings, source)
    copyfile = backup_module.shutil.copyfile

    def corrupt_copy(src, dst, **kwargs):
        result = copyfile(src, dst, **kwargs)
        if Path(dst).name == "ledger.sqlite3":
            with sqlite3.connect(dst) as database:
                # Valid SQLite with valid canonical hashes, but not the source snapshot.
                database.execute("PRAGMA user_version=42")
        return result

    monkeypatch.setattr(backup_module.shutil, "copyfile", corrupt_copy)
    with pytest.raises(ValueError, match="copy checksum"):
        restore(source, destination)
    assert not destination.exists()


def test_backup_restore_actual_wal_snapshot_in_isolated_fixture(tmp_path, monkeypatch):
    # Exercise actual WAL connections and backup bytes, not a fake SQLite connection.
    # Gate approval is mocked ONLY in this single-test, no-worker fixture on old runtimes.
    # Production wal_is_fixed remains enforced and has its existing independent tests.
    monkeypatch.setattr(sqlite_store, "wal_is_fixed", lambda: True)
    settings = Settings(data_root=tmp_path / "workspace", journal_mode="WAL")
    settings.prepare_directories()
    old = populated_legacy(settings.database)
    before = frozen_rows(old.db)
    old.close()
    migrate(settings.database)
    writer = Store(settings.database, journal_mode="WAL")
    try:
        assert writer.db.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
        source = tmp_path / "backup"
        backup(settings, source)
        assert writer.db.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
    finally:
        writer.close()
    with sqlite3.connect(source / "ledger.sqlite3") as snapshot:
        assert snapshot.execute("PRAGMA journal_mode").fetchone()[0] == "delete"
        assert frozen_rows(snapshot) == before
    assert not (source / "ledger.sqlite3-wal").exists()
    restored = tmp_path / "restored"
    assert restore(source, restored)["restored"]
    with sqlite3.connect(restored / "db" / "ledger.sqlite3") as database:
        assert frozen_rows(database) == before
