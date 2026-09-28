"""Current candidate metadata must not retain stale historical release claims."""

from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

from statement_ledger.contracts.models import KINDS

ROOT = Path(__file__).resolve().parents[1]


def test_release_metadata_matches_the_current_repository():
    release = json.loads((ROOT / "RELEASE.json").read_text(encoding="utf-8"))
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    sources = json.loads((ROOT / "src/statement_ledger/sources.json").read_text(encoding="utf-8"))
    assert release["version"] == project["project"]["version"]
    assert release["status"] == "pull_request_candidate"
    assert release["remote_repository_created"] is True
    assert release["source_registry_entries"] == len(sources)
    assert release["source_worksheets"] == len(list((ROOT / "docs/sources").glob("*.md")))
    assert release["record_schemas"] == len(KINDS)
    assert release["engineering_tickets"] == len(list((ROOT / "tickets").glob("SL-*.md")))
    assert release["architecture_decisions"] == len(list((ROOT / "docs/adr").glob("*.md")))
    spec = (ROOT / "SPECIFICATION.md").read_text(encoding="utf-8")
    assert release["specification_chapters"] == len(re.findall(r"^## \d+\.", spec, re.MULTILINE))
    for key in ("status_document", "method_and_limitations", "historical_release_manifest"):
        assert (ROOT / release["validation"][key]).is_file()
    historical = json.loads(
        (ROOT / release["validation"]["historical_release_manifest"]).read_text()
    )
    assert historical["version"] == "0.2.0"
    assert historical["remote_repository_created"] is False
    assert (
        "tests_passed" not in release
    )  # Count belongs to an exact tested commit, not a moving file.
    assert "statement_coverage_percent" not in release
