"""Load exact, frozen v0.2 Store code; never derive the old schema from current SQL."""

from __future__ import annotations

import hashlib
import sys
import types
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).parent / "fixtures" / "v02"
BLOBS = {
    "store": "9482e9ace420d09bd17b785671d97af281cbe71d",
    "util": "f516e4a030a70e9e87c9311a3a89026b16e1760f",
    "jobs": "fa8ccfa8f98493b8fdc0dca51fdb7cdf2a7d2931",
}


def legacy_types():
    namespace = "_statement_ledger_frozen_v02"
    package = types.ModuleType(namespace)
    package.__path__ = [str(ROOT)]
    sys.modules[namespace] = package
    # Store imports only models.now. Use a fixed clock without loading today's models.
    models = types.ModuleType(namespace + ".models")
    models.now = lambda: datetime(2026, 9, 1, tzinfo=UTC)
    sys.modules[models.__name__] = models
    for name in ("util", "store", "jobs"):
        raw = (ROOT / (name + ".py.txt")).read_bytes()
        assert (
            hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == BLOBS[name]
        )
        module = types.ModuleType(namespace + "." + name)
        module.__file__ = str(ROOT / (name + ".py.txt"))
        module.__package__ = namespace
        sys.modules[module.__name__] = module
        exec(compile(raw, module.__file__, "exec"), module.__dict__)
    return sys.modules[namespace + ".store"].Store, sys.modules[namespace + ".jobs"].JobQueue


def populated_legacy(path, *, job_state="succeeded"):
    OldStore, OldQueue = legacy_types()
    store = OldStore(path)
    with store.transaction():
        person = store.write(
            "person",
            {"id": "fixture-person", "display_name": "Fictional Legacy Person"},
            [],
            0,
            "frozen-v02-fixture",
        )
        store.write(
            "proposition",
            {
                "id": "fixture-claim",
                "text": "Synthetic sample count is 10.",
                "scope": {"entity": "Synthetic Lab", "period": "2025"},
            },
            [{"kind": "person", "id": person["id"], "revision": 1}],
            0,
            "frozen-v02-fixture",
        )
        store.write(
            "person",
            {"id": "fixture-person", "display_name": "Fictional Corrected Name"},
            [],
            1,
            "frozen-v02-fixture",
        )
    store.capture_provider_response(
        "a" * 64, 1, 200, b'{"synthetic":true}', False, {"source": "fixture"}
    )
    queue = OldQueue(path)  # The real legacy jobs table is INSIDE the canonical database.
    job_id = queue.enqueue({"task": "synthetic-local-fixture"})
    if job_state == "succeeded":
        job = queue.claim()
        queue.finish(job_id, job["lease_token"], {"synthetic": True})
    elif job_state == "failed":
        queue.db.execute("UPDATE jobs SET state='failed' WHERE id=?", (job_id,))
    queue.close()
    return store


def frozen_rows(connection):
    tables = (
        "revisions",
        "heads",
        "dependencies",
        "audit",
        "outbox",
        "provider_receipts",
        "schema_migrations",
        "jobs",
        "claim_search",
    )
    return {
        table: sorted(
            [tuple(row) for row in connection.execute('SELECT * FROM "' + table + '"')], key=repr
        )
        for table in tables
    }
