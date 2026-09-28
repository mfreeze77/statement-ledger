"""Consistent database plus immutable registered artifacts; restore never overwrites a workspace."""

from __future__ import annotations

import hashlib
import json
import shutil
import sqlite3
import time
from pathlib import Path
from typing import Any

from statement_ledger.infrastructure.artifacts import Artifact, LocalArtifactStore
from statement_ledger.infrastructure.migrations import check_schema
from statement_ledger.infrastructure.settings import Settings
from statement_ledger.infrastructure.sqlite_store import Store


def checksum(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def backup(settings: Settings, destination: Path) -> dict[str, Any]:
    if destination.exists():
        raise ValueError("Backup destination must not exist")
    destination.mkdir(parents=True)
    store = None
    try:
        store = Store(settings.database, journal_mode=settings.journal_mode)
        artifacts = LocalArtifactStore(settings.artifacts)
        # A writer reservation freezes accepted references and stops concurrent result commits.
        with store.transaction():
            active = store.db.execute(
                "SELECT count(*) FROM work_jobs WHERE state='running'"
            ).fetchone()[0]
            if active:
                raise ValueError("Stop workers or wait for running jobs before a workspace backup")
            database_path = destination / "ledger.sqlite3"
            reader = sqlite3.connect(settings.database.resolve().as_uri() + "?mode=ro", uri=True)
            output = sqlite3.connect(database_path)
            try:
                reader.backup(output)
                # A portable snapshot must not depend on WAL/SHM sidecars. Source stays unchanged.
                output.execute("PRAGMA journal_mode=DELETE")
            finally:
                output.close()
                reader.close()
            (destination / "artifacts").mkdir()
            entries = []
            for row in store.db.execute(
                "SELECT key,sha256,size FROM artifact_refs ORDER BY key"
            ).fetchall():
                artifact = Artifact(**dict(row))
                artifacts.verify(artifact)
                path = destination / "artifacts" / artifact.key
                path.parent.mkdir(parents=True, exist_ok=True)
                with artifacts.open(artifact.key) as source, path.open("wb") as target:
                    shutil.copyfileobj(source, target)
                if checksum(path) != artifact.sha256:
                    raise ValueError("Artifact changed while backing up")
                entries.append(artifact.as_dict())
            manifest = {
                "format": "statement-ledger-workspace-v1",
                "created_at": time.time(),
                "database_sha256": checksum(database_path),
                "artifacts": entries,
                "scope": "canonical_database_and_registered_artifacts",
                "excluded": [
                    "unregistered external files",
                    "model cache",
                    "scratch",
                    "other backups",
                ],
                "notice": "Private evidence backup. Register media/raw/evaluation inputs before relying on this backup for those bytes.",
            }
            (destination / "manifest.json").write_text(
                json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
            )
        return manifest
    except BaseException:
        shutil.rmtree(destination)
        raise
    finally:
        if store is not None:
            store.close()


def restore(source: Path, destination: Path) -> dict[str, Any]:
    if destination.exists():
        raise ValueError("Restore destination must not exist; never overwrite live data")
    if (
        source.is_symlink()
        or (source / "manifest.json").is_symlink()
        or (source / "ledger.sqlite3").is_symlink()
    ):
        raise ValueError("Backup symlinks are not accepted")
    manifest = json.loads((source / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("format") != "statement-ledger-workspace-v1" or checksum(
        source / "ledger.sqlite3"
    ) != manifest.get("database_sha256"):
        raise ValueError("Backup manifest/database checksum mismatch")
    source_store = LocalArtifactStore(source / "artifacts", readonly=True)
    for entry in manifest["artifacts"]:
        source_store.verify(Artifact(**entry))
    database = sqlite3.connect(
        (source / "ledger.sqlite3").resolve().as_uri() + "?mode=ro", uri=True
    )
    try:
        check_schema(database)
        if database.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise ValueError("Backup database is corrupt")
        references = {
            row[0]: (row[1], row[2])
            for row in database.execute("SELECT key,sha256,size FROM artifact_refs")
        }
        expected = {
            entry["key"]: (entry["sha256"], entry["size"]) for entry in manifest["artifacts"]
        }
        if references != expected:
            raise ValueError("Artifact manifest does not match canonical references")
    finally:
        database.close()
    try:
        (destination / "db").mkdir(parents=True)
        copied_database = destination / "db" / "ledger.sqlite3"
        shutil.copyfile(source / "ledger.sqlite3", copied_database)
        if checksum(copied_database) != manifest["database_sha256"]:
            raise ValueError("Restored database copy checksum mismatch")
        target_store = LocalArtifactStore(destination / "artifacts")
        for entry in manifest["artifacts"]:
            with source_store.open(entry["key"]) as stream:
                artifact = target_store.put(stream)
            if artifact.as_dict() != entry:
                raise ValueError("Restored artifact differs from its manifest")
        store = Store(destination / "db" / "ledger.sqlite3")
        try:
            valid = (
                store.verify_records()["valid"]
                and store.verify_audit()["valid"]
                and store.verify_provider_receipts()["valid"]
            )
            if not valid:
                raise ValueError("Restored canonical audit/record verification failed")
        finally:
            store.close()
        return {
            "restored": True,
            "destination": str(destination),
            "artifacts": len(manifest["artifacts"]),
            "records_and_audit_verified": True,
        }
    except BaseException:
        shutil.rmtree(destination)
        raise
