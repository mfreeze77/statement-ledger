"""Transactional, append-only record revisions with dependency-driven invalidation.

SQLite is the single-workspace reference store, not the production tenancy design.
The dependency index is operational provenance, not a replacement semantic graph.
"""

from __future__ import annotations

import base64
import hashlib
import json
import uuid
from contextlib import contextmanager
from importlib.resources import files
from pathlib import Path
from threading import RLock
from typing import Any

from statement_ledger.contracts.models import now
from statement_ledger.core.errors import Conflict, Missing
from statement_ledger.core.util import canonical_json, digest
from statement_ledger.infrastructure.migrations import (
    MigrationError,
    check_schema,
    migrate,
    migrate_connection,
    open_database,
    wal_is_fixed,
)

SCHEMA = (
    files("statement_ledger.infrastructure.migrations")
    .joinpath("001_core.sql")
    .read_text(encoding="utf-8")
)


class Store:
    def __init__(self, path: str | Path, *, initialize: bool = False, journal_mode: str = "DELETE"):
        self.lock = RLock()
        self.path = str(path)
        self._savepoint = 0
        if initialize and self.path != ":memory:":
            migrate(path)
        self.db = open_database(path)
        try:
            if initialize and self.path == ":memory:":
                migrate_connection(self.db)
            check_schema(self.db)
            if journal_mode not in {"DELETE", "WAL"}:
                raise ValueError("Unsupported journal mode")
            if journal_mode == "WAL" and not wal_is_fixed():
                raise MigrationError(
                    "WAL workers require SQLite 3.51.3+ or the documented fixed backports; use DELETE mode"
                )
            self.db.execute("PRAGMA journal_mode=" + journal_mode)
        except BaseException:
            self.db.close()
            raise

    @contextmanager
    def transaction(self):
        with self.lock:
            nested = self.db.in_transaction
            self._savepoint += 1
            name = "ledger_" + str(self._savepoint)
            self.db.execute("SAVEPOINT " + name if nested else "BEGIN IMMEDIATE")
            try:
                yield
            except BaseException:
                if nested:
                    self.db.execute("ROLLBACK TO SAVEPOINT " + name)
                    self.db.execute("RELEASE SAVEPOINT " + name)
                else:
                    self.db.rollback()
                raise
            else:
                if nested:
                    self.db.execute("RELEASE SAVEPOINT " + name)
                else:
                    self.db.commit()

    def search_propositions(self, expression: str, limit: int):
        return self.db.execute(
            "SELECT proposition_id,bm25(claim_search) AS relevance FROM claim_search WHERE claim_search MATCH ? ORDER BY relevance,proposition_id LIMIT ?",
            (expression, limit),
        ).fetchall()

    def _rebuild_claim_index(self):
        self.db.execute("DELETE FROM claim_search")
        for row in self.db.execute(
            "SELECT r.payload FROM heads h JOIN revisions r USING(kind,id,revision) WHERE h.kind='proposition'"
        ).fetchall():
            p = json.loads(row[0])
            self._index_proposition(p)

    def rebuild_claim_index(self):
        with self.transaction():
            self._rebuild_claim_index()
        return {
            "indexed": self.db.execute("SELECT count(*) FROM claim_search").fetchone()[0],
            "index": "sqlite-fts5",
        }

    def _index_proposition(self, payload):
        self.db.execute("DELETE FROM claim_search WHERE proposition_id=?", (payload["id"],))
        self.db.execute(
            "INSERT INTO claim_search VALUES(?,?,?)",
            (payload["id"], payload["text"], canonical_json(payload["scope"])),
        )

    def capture_provider_response(self, request_hash, attempt, status, body, truncated, request):
        rid = "receipt-" + uuid.uuid4().hex
        fingerprint = hashlib.sha256(body).hexdigest()
        with self.transaction():
            self.db.execute(
                "INSERT INTO provider_receipts VALUES(?,?,?,?,?,?,?,?,?)",
                (
                    rid,
                    request_hash,
                    attempt,
                    status,
                    body,
                    fingerprint,
                    int(truncated),
                    now().isoformat(),
                    canonical_json(request),
                ),
            )
            self.audit(
                {
                    "type": "provider.response_captured",
                    "id": rid,
                    "request_hash": request_hash,
                    "response_sha256": fingerprint,
                    "http_status": status,
                    "truncated": truncated,
                }
            )
        return rid

    def provider_receipt(self, rid):
        row = self.db.execute("SELECT * FROM provider_receipts WHERE id=?", (rid,)).fetchone()
        if not row:
            raise Missing(f"provider_receipt:{rid}")
        out = dict(row)
        out["request_metadata"] = json.loads(out["request_metadata"])
        return out

    def find_decisions(self, request_hash):
        rows = self.db.execute(
            """SELECT r.id FROM revisions r JOIN heads h USING(kind,id,revision)
            WHERE r.kind='decision_run' AND json_extract(r.payload,'$.request_hash')=?
            ORDER BY r.created_at DESC LIMIT 20""",
            (request_hash,),
        ).fetchall()
        return [self.get("decision_run", r[0]) for r in rows]

    def records_for_proposition(self, kind, proposition_id):
        rows = self.db.execute(
            """SELECT r.id FROM revisions r JOIN heads h USING(kind,id,revision)
            WHERE r.kind=? AND json_extract(r.payload,'$.proposition_id')=? ORDER BY r.id""",
            (kind, proposition_id),
        ).fetchall()
        return [self.get(kind, r[0]) for r in rows]

    def corrections_for_targets(self, keys):
        out = []
        for kind, rid in sorted(keys):
            rows = self.db.execute(
                """SELECT r.id FROM revisions r JOIN heads h USING(kind,id,revision)
                WHERE r.kind='correction' AND json_extract(r.payload,'$.target_kind')=?
                AND json_extract(r.payload,'$.target_id')=?""",
                (kind, rid),
            ).fetchall()
            out.extend(self.get("correction", r[0]) for r in rows)
        return out

    def verify_provider_receipts(self) -> dict[str, Any]:
        count = 0
        for r in self.db.execute("SELECT id,body,body_sha256 FROM provider_receipts"):
            if hashlib.sha256(r["body"]).hexdigest() != r["body_sha256"]:
                return {"valid": False, "checked": count, "failed_receipt": r["id"]}
            count += 1
        return {"valid": True, "checked": count}

    def close(self) -> None:
        self.db.close()

    def get(self, kind: str, record_id: str, revision: int | None = None) -> dict:
        if revision is None:
            row = self.db.execute(
                """SELECT r.*,h.stale,h.stale_reason FROM heads h
                JOIN revisions r USING(kind,id,revision) WHERE h.kind=? AND h.id=?""",
                (kind, record_id),
            ).fetchone()
        else:
            row = self.db.execute(
                "SELECT *,0 AS stale,NULL AS stale_reason FROM revisions WHERE kind=? AND id=? AND revision=?",
                (kind, record_id, revision),
            ).fetchone()
        if row is None:
            raise Missing(f"{kind}:{record_id}")
        out = dict(row)
        out["payload"] = json.loads(out["payload"])
        out["dependencies"] = json.loads(out["dependencies"])
        out["stale"] = bool(out["stale"])
        out["historical_revision"] = revision is not None
        return out

    def list(self, kind: str, limit: int = 100, offset: int = 0) -> list[dict]:
        if not 1 <= limit <= 1000 or offset < 0:
            raise ValueError("limit must be 1..1000; offset must be nonnegative")
        ids = self.db.execute(
            "SELECT id FROM heads WHERE kind=? ORDER BY id LIMIT ? OFFSET ?", (kind, limit, offset)
        )
        return [self.get(kind, row["id"]) for row in ids.fetchall()]

    def all(self, kind: str) -> list[dict]:
        # Reference UI only; production needs bounded query-specific projections.
        ids = self.db.execute("SELECT id FROM heads WHERE kind=? ORDER BY id", (kind,)).fetchall()
        return [self.get(kind, row["id"]) for row in ids]

    def counts(self) -> dict[str, int]:
        return dict(self.db.execute("SELECT kind,count(*) FROM heads GROUP BY kind").fetchall())

    def would_cycle(self, child: tuple[str, str], parent: tuple[str, str]) -> bool:
        todo, seen = [parent], set()
        while todo:
            node = todo.pop()
            if node == child:
                return True
            if node in seen:
                continue
            seen.add(node)
            todo.extend(
                tuple(r)
                for r in self.db.execute(
                    "SELECT parent_kind,parent_id FROM dependencies WHERE child_kind=? AND child_id=?",
                    node,
                )
            )
        return False

    def write(
        self, kind: str, payload: dict, deps: list[dict], expected_revision: int, actor: str
    ) -> dict:
        """Call inside transaction after service validation; direct use is internal only."""
        record_id = payload["id"]
        stamp = now().isoformat()
        head = self.db.execute(
            "SELECT revision FROM heads WHERE kind=? AND id=?", (kind, record_id)
        ).fetchone()
        current = int(head[0]) if head else 0
        fingerprint = digest({"payload": payload, "dependencies": deps})
        if current != expected_revision:
            raise Conflict(f"Revision conflict: expected {expected_revision}, current {current}")
        if current:
            old = self.get(kind, record_id)
            if old["hash"] == fingerprint and not old["stale"]:
                return old
        if current != expected_revision:
            raise Conflict(f"Revision conflict: expected {expected_revision}, current {current}")
        revision = current + 1
        self.db.execute(
            "INSERT INTO revisions VALUES (?,?,?,?,?,?,?,?)",
            (
                kind,
                record_id,
                revision,
                canonical_json(payload),
                fingerprint,
                canonical_json(deps),
                stamp,
                actor,
            ),
        )
        self.db.execute(
            "INSERT INTO heads VALUES (?,?,?,0,NULL) ON CONFLICT(kind,id) DO UPDATE SET revision=excluded.revision,stale=0,stale_reason=NULL",
            (kind, record_id, revision),
        )
        self.db.execute(
            "DELETE FROM dependencies WHERE child_kind=? AND child_id=?", (kind, record_id)
        )
        for dep in deps:
            self.db.execute(
                "INSERT INTO dependencies VALUES (?,?,?,?,?)",
                (kind, record_id, dep["kind"], dep["id"], dep["revision"]),
            )
        invalidated = []
        if current:
            todo, seen = [(kind, record_id)], {(kind, record_id)}
            while todo:
                parent = todo.pop()
                children = self.db.execute(
                    "SELECT child_kind,child_id FROM dependencies WHERE parent_kind=? AND parent_id=?",
                    parent,
                ).fetchall()
                for child in map(tuple, children):
                    if child in seen:
                        continue
                    seen.add(child)
                    todo.append(child)
                    invalidated.append(child)
                    self.db.execute(
                        "UPDATE heads SET stale=1,stale_reason=? WHERE kind=? AND id=?",
                        (f"Changed dependency {kind}:{record_id}@{revision}", *child),
                    )
        event = {
            "type": "record.revised" if current else "record.created",
            "kind": kind,
            "id": record_id,
            "revision": revision,
            "record_hash": fingerprint,
            "actor": actor,
            "at": stamp,
            "invalidated": invalidated,
        }
        if kind == "proposition":
            self._index_proposition(payload)
        self.audit(event)
        self.db.execute("INSERT INTO outbox(event) VALUES (?)", (canonical_json(event),))
        return self.get(kind, record_id)

    def audit(self, event: dict[str, Any]):
        last = self.db.execute("SELECT hash FROM audit ORDER BY sequence DESC LIMIT 1").fetchone()
        previous = last[0] if last else "0" * 64
        self.db.execute(
            "INSERT INTO audit(event,previous_hash,hash) VALUES (?,?,?)",
            (canonical_json(event), previous, digest({"previous": previous, "event": event})),
        )

    def verify_audit(self) -> dict:
        previous, count = "0" * 64, 0
        for row in self.db.execute("SELECT * FROM audit ORDER BY sequence"):
            event = json.loads(row["event"])
            if row["previous_hash"] != previous or row["hash"] != digest(
                {"previous": previous, "event": event}
            ):
                return {"valid": False, "checked": count, "failed_sequence": row["sequence"]}
            previous, count = row["hash"], count + 1
        return {
            "valid": True,
            "checked": count,
            "head_hash": previous,
            "externally_anchored": False,
        }

    def verify_records(self) -> dict:
        count = 0
        for row in self.db.execute("SELECT * FROM revisions"):
            if (
                digest(
                    {
                        "payload": json.loads(row["payload"]),
                        "dependencies": json.loads(row["dependencies"]),
                    }
                )
                != row["hash"]
            ):
                return {
                    "valid": False,
                    "checked": count,
                    "failed_record": f"{row['kind']}:{row['id']}@{row['revision']}",
                }
            count += 1
        return {"valid": True, "checked": count}

    def history(self, kind: str, record_id: str) -> list[dict]:
        numbers = self.db.execute(
            "SELECT revision FROM revisions WHERE kind=? AND id=? ORDER BY revision",
            (kind, record_id),
        ).fetchall()
        if not numbers:
            raise Missing(f"{kind}:{record_id}")
        return [self.get(kind, record_id, int(r[0])) for r in numbers]

    def export(self) -> dict:
        rows = []
        for kind, rid, revision in self.db.execute(
            "SELECT kind,id,revision FROM revisions ORDER BY kind,id,revision"
        ).fetchall():
            rows.append(self.get(kind, rid, revision))
        return {
            "format": "statement-ledger-backup-v2",
            "records": rows,
            "heads": [dict(r) for r in self.db.execute("SELECT * FROM heads ORDER BY kind,id")],
            "audit": [dict(r) for r in self.db.execute("SELECT * FROM audit ORDER BY sequence")],
            "provider_receipts": [
                {
                    **{k: v for k, v in dict(r).items() if k != "body"},
                    "body_base64": base64.b64encode(bytes(r["body"])).decode("ascii"),
                }
                for r in self.db.execute("SELECT * FROM provider_receipts")
            ],
            "notice": "Private operator backup; raw provider responses and request text may be sensitive; rights must be rechecked before sharing.",
        }
