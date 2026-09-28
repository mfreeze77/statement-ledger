"""Bounded file ingestion with content-addressed archive and an honest receipt."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from statement_ledger.core.errors import Missing
from statement_ledger.infrastructure.ingestion import archive_file, iter_rows, read_document
from statement_ledger.pillars.discovery.parsers import parse


def ingest_file(
    ledger,
    path: Path,
    source_id: str,
    rights_id: str,
    *,
    archive_root: Path,
    mode: str = "jsonl",
    max_records: int = 10000,
    actor: str = "local-operator",
) -> dict:
    from statement_ledger.contracts.models import RightsGrant
    from statement_ledger.core.policy import require_right

    grant = RightsGrant.model_validate(ledger.store.get("rights", rights_id)["payload"])
    # Manual envelopes may name a different actual source, validated per observation.
    require_right(grant, "store_text", None if source_id == "manual_import" else source_id)
    if not path.is_file():
        raise ValueError("Input file must exist")
    if max_records < 1:
        raise ValueError("max_records must be positive")
    if mode not in {"jsonl", "json"}:
        raise ValueError("mode must be jsonl or json")
    sha, stored = archive_file(path, archive_root)
    # Parse retained bytes with original compression suffix without another source-file read.
    compressed = path.suffix if path.suffix in {".gz", ".bz2"} else ""
    temp = stored.with_name(stored.name + compressed) if compressed else stored
    if compressed and not temp.exists():
        try:
            os.link(stored, temp)
        except OSError:
            shutil.copyfile(stored, temp)
    if mode == "json":
        doc = read_document(temp)
        rows = doc if isinstance(doc, list) else [doc]
        rows = iter(rows[:max_records])
    else:
        rows = iter_rows(temp, max_records=max_records)
    result = {
        "file_sha256": sha,
        "archive_path": str(stored),
        "rows_read": 0,
        "created": 0,
        "revised": 0,
        "unchanged": 0,
        "errors": [],
        "record_limit": max_records,
        "completion": "unknown_until_end",
    }
    try:
        for number, row in enumerate(rows, 1):
            result["rows_read"] += 1
            try:
                observations = parse(source_id, row, rights_id)
                for obs in observations:
                    p = obs.model_dump(mode="json")
                    try:
                        old = ledger.store.get("observation", obs.id)
                        revision = old["revision"]
                        comparison = dict(p)
                        comparison["retrieved_at"] = old["payload"]["retrieved_at"]
                        if comparison == old["payload"] and ledger.dependencies_current(
                            "observation", obs.id
                        ):
                            result["unchanged"] += 1
                            continue
                    except Missing:
                        revision = 0
                    ledger.put("observation", p, revision, actor)
                    result["revised" if revision else "created"] += 1
            except (ValueError, KeyError) as exc:
                # Raw source stays in archive; error is per physical source row, not silently skipped.
                result["errors"].append(
                    {"row": number, "error_type": type(exc).__name__, "message": str(exc)[:500]}
                )
        result["completion"] = "bounded_or_eof" if result["rows_read"] >= max_records else "eof"
    except (ValueError, UnicodeError, EOFError, OSError) as exc:
        result["errors"].append(
            {
                "row": result["rows_read"] + 1,
                "error_type": type(exc).__name__,
                "message": str(exc)[:500],
            }
        )
        result["completion"] = "parse_failed_partial_commit"
    result["success"] = not result["errors"]
    return result
