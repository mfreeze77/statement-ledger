"""SQL-first, transactional migrations. Runtime opens never silently upgrade a database."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from collections.abc import Callable
from datetime import UTC, datetime
from importlib.resources import files
from pathlib import Path

LATEST_VERSION = 3
CORE_COLUMNS = {
    "revisions": {
        "kind",
        "id",
        "revision",
        "payload",
        "hash",
        "dependencies",
        "created_at",
        "actor",
    },
    "heads": {"kind", "id", "revision", "stale", "stale_reason"},
    "dependencies": {"child_kind", "child_id", "parent_kind", "parent_id", "parent_revision"},
    "audit": {"sequence", "event", "previous_hash", "hash"},
    "outbox": {"sequence", "event", "state"},
}


class MigrationError(RuntimeError):
    pass


def scripts() -> list[tuple[int, str, str, str]]:
    root = files(__package__)
    result = []
    for item in sorted(root.iterdir(), key=lambda p: p.name):
        if item.name.endswith(".sql"):
            text = item.read_text(encoding="utf-8")
            result.append(
                (
                    int(item.name.split("_", 1)[0]),
                    item.name,
                    text,
                    hashlib.sha256(text.encode()).hexdigest(),
                )
            )
    if [row[0] for row in result] != list(range(1, LATEST_VERSION + 1)):
        raise MigrationError("Migration inventory is incomplete")
    return result


def execute_sql(connection: sqlite3.Connection, sql: str) -> None:
    # executescript implicitly commits: never use it inside a migration transaction.
    pending = ""
    for line in sql.splitlines(keepends=True):
        pending += line
        if sqlite3.complete_statement(pending):
            connection.execute(pending)
            pending = ""
    if pending.strip():
        raise MigrationError("Incomplete migration SQL")


def wal_is_fixed(version: tuple[int, ...] | None = None) -> bool:
    actual = version or sqlite3.sqlite_version_info
    return (
        actual >= (3, 51, 3)
        or (3, 50, 7) <= actual < (3, 51, 0)
        or (3, 44, 6) <= actual < (3, 45, 0)
    )


def open_database(path: str | Path) -> sqlite3.Connection:
    if str(path) != ":memory:" and not Path(path).is_file():
        raise MigrationError("Database is not initialized; run statement-ledger migrate")
    uri = Path(path).resolve().as_uri() + "?mode=rw" if str(path) != ":memory:" else ":memory:"
    connection = sqlite3.connect(
        uri, uri=str(path) != ":memory:", isolation_level=None, timeout=30, check_same_thread=False
    )
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys=ON")
    return connection


def _tables(connection: sqlite3.Connection) -> set[str]:
    return {
        row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }


def _check_legacy_jobs(connection: sqlite3.Connection) -> None:
    if "jobs" not in _tables(connection):
        return
    columns = {row[1] for row in connection.execute('PRAGMA table_info("jobs")')}
    if "state" not in columns:
        raise MigrationError("Unrecognized legacy jobs schema; manual reconciliation is required")
    count = connection.execute(
        "SELECT count(*) FROM jobs WHERE state IS NULL OR state NOT IN ('succeeded','failed','cancelled')"
    ).fetchone()[0]
    if count:
        raise MigrationError(
            "Legacy jobs have non-terminal records; export and reconcile them before migration. "
            "Finished jobs are retained unchanged."
        )


def _legacy_check(connection: sqlite3.Connection) -> None:
    tables = _tables(connection)
    _check_legacy_jobs(connection)
    if tables & set(CORE_COLUMNS) and not set(CORE_COLUMNS) <= tables:
        raise MigrationError("Partial or unknown legacy database layout")
    if tables and not set(CORE_COLUMNS) <= tables and "foundation_migrations" not in tables:
        raise MigrationError("Not a recognized Statement Ledger database")
    for table, expected in CORE_COLUMNS.items():
        if table in tables:
            columns = {row[1] for row in connection.execute(f'PRAGMA table_info("{table}")')}
            if columns != expected:
                raise MigrationError(f"Unexpected legacy columns: {table}")
    if "schema_migrations" in tables:
        versions = {row[0] for row in connection.execute("SELECT version FROM schema_migrations")}
        if versions - {2}:
            raise MigrationError("Unrecognized legacy schema version")


def check_schema(connection: sqlite3.Connection) -> None:
    if "foundation_migrations" not in _tables(connection):
        raise MigrationError("Legacy or empty schema; run statement-ledger migrate")
    expected = {version: (name, checksum) for version, name, _, checksum in scripts()}
    actual = {
        row[0]: (row[1], row[2])
        for row in connection.execute("SELECT version,name,sha256 FROM foundation_migrations")
    }
    if actual != expected:
        raise MigrationError(
            "Migration version/checksum mismatch; run migrate with the matching application version"
        )
    _legacy_check(connection)
    required = {
        "work_jobs",
        "work_attempts",
        "artifact_refs",
        "job_artifacts",
        "provider_operations",
        "claim_search",
        "provider_receipts",
        "schema_migrations",
    } | set(CORE_COLUMNS)
    if not required <= _tables(connection):
        raise MigrationError("Database is missing required core or runtime tables")


def migrate_connection(
    connection: sqlite3.Connection, *, before_version: Callable[[int], None] | None = None
) -> dict[str, object]:
    connection.execute("PRAGMA foreign_keys=ON")
    connection.execute("BEGIN EXCLUSIVE")
    applied: list[int] = []
    try:
        _legacy_check(connection)
        connection.execute(
            "CREATE TABLE IF NOT EXISTS foundation_migrations(version INTEGER PRIMARY KEY,name TEXT NOT NULL,sha256 TEXT NOT NULL,applied_at TEXT NOT NULL)"
        )
        inventory = scripts()
        known = {item[0]: item for item in inventory}
        existing = {
            row[0]: (row[1], row[2])
            for row in connection.execute("SELECT version,name,sha256 FROM foundation_migrations")
        }
        for version, (name, checksum) in existing.items():
            if version not in known or (name, checksum) != (known[version][1], known[version][3]):
                raise MigrationError("Unknown version or modified applied migration")
        if sorted(existing) != list(range(1, len(existing) + 1)):
            raise MigrationError("Migration history contains a gap")
        for version, name, sql, checksum in inventory:
            if version in existing:
                continue
            if before_version is not None:
                before_version(version)
            execute_sql(connection, sql)
            if version == 2:
                connection.execute("DELETE FROM claim_search")
                for row in connection.execute(
                    "SELECT r.payload FROM heads h JOIN revisions r USING(kind,id,revision) WHERE h.kind='proposition'"
                ).fetchall():
                    payload = json.loads(row[0])
                    scope = json.dumps(
                        payload["scope"],
                        sort_keys=True,
                        separators=(",", ":"),
                        ensure_ascii=False,
                        allow_nan=False,
                    )
                    connection.execute(
                        "INSERT INTO claim_search VALUES(?,?,?)",
                        (payload["id"], payload["text"], scope),
                    )
                connection.execute(
                    "INSERT OR IGNORE INTO schema_migrations VALUES(2,?)",
                    (datetime.now(UTC).isoformat(),),
                )
            connection.execute(
                "INSERT INTO foundation_migrations VALUES(?,?,?,?)",
                (version, name, checksum, datetime.now(UTC).isoformat()),
            )
            applied.append(version)
        check_schema(connection)
        if connection.execute("PRAGMA foreign_key_check").fetchone() is not None:
            raise MigrationError("Foreign-key integrity check failed")
        connection.commit()
        return {
            "schema_version": LATEST_VERSION,
            "applied": applied,
            "canonical_records_rewritten": False,
        }
    except BaseException:
        connection.rollback()
        raise


def migrate(
    path: str | Path,
    *,
    legacy_jobs_path: Path | None = None,
    before_version: Callable[[int], None] | None = None,
) -> dict[str, object]:
    if str(path) == ":memory:":
        raise MigrationError("Use migrate_connection for an in-memory database")
    path = Path(path)
    if (
        legacy_jobs_path is not None
        and legacy_jobs_path.exists()
        and legacy_jobs_path.resolve() != path.resolve()
    ):
        with sqlite3.connect(legacy_jobs_path.resolve().as_uri() + "?mode=ro", uri=True) as legacy:
            try:
                _check_legacy_jobs(legacy)
            except MigrationError as exc:
                raise MigrationError("A separate legacy jobs database: " + str(exc)) from None
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, isolation_level=None, timeout=30)
    try:
        return migrate_connection(connection, before_version=before_version)
    finally:
        connection.close()
