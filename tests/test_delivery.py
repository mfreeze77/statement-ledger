"""Delivery consistency and publishing isolation tests; no remote calls."""

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from statement_ledger.models import KINDS

ROOT = Path(__file__).resolve().parents[1]


def test_generated_schemas_match_models():
    for kind, model in KINDS.items():
        assert (
            json.loads((ROOT / "contracts" / f"{kind}.schema.json").read_text())
            == model.model_json_schema()
        )


def test_backlog_links_and_dependency_graph():
    records = json.loads((ROOT / "tickets/tickets.json").read_text())
    items = {x["id"]: x for x in records}
    assert len(items) == len(records)
    for r in records:
        assert (ROOT / r["path"]).is_file()
        assert set(r["dependencies"]) <= items.keys()

    def visit(key, ancestors):
        assert key not in ancestors, "Cyclic ticket dependencies"
        for dep in items[key]["dependencies"]:
            visit(dep, ancestors | {key})

    for key in items:
        visit(key, set())


def test_all_registered_sources_have_worksheets():
    records = json.loads((ROOT / "src/statement_ledger/sources.json").read_text())
    assert len({r["id"] for r in records}) == len(records)
    for r in records:
        assert (ROOT / "docs/sources" / f"{r['id']}.md").is_file()


def test_internal_document_links_exist():
    bad = []
    for p in [
        ROOT / "README.md",
        ROOT / "AGENTS.md",
        ROOT / "KICKOFF_PROMPT.md",
        *list((ROOT / "docs").rglob("*.md")),
        *list((ROOT / "tickets").glob("*.md")),
    ]:
        for link in re.findall(r"\]\(([^)]+)\)", p.read_text()):
            link = link.split("#", 1)[0]
            if not link or "://" in link or link.startswith("mailto:"):
                continue
            if not (p.parent / link).exists():
                bad.append(f"{p.relative_to(ROOT)}: {link}")
    assert not bad, bad


@pytest.mark.skipif(
    not shutil.which("git") or not shutil.which("bash"), reason="Git and Bash required"
)
def test_publish_refuses_a_parent_repository(tmp_path):
    parent = tmp_path / "parent"
    parent.mkdir()
    subprocess.run(["git", "init", "-q", str(parent)], check=True)
    child = parent / "independent"
    (child / "scripts").mkdir(parents=True)
    shutil.copy(ROOT / "scripts/publish-github.sh", child / "scripts/publish-github.sh")
    result = subprocess.run(
        ["bash", str(child / "scripts/publish-github.sh")], text=True, capture_output=True
    )
    assert result.returncode != 0
    assert "different Git repository" in result.stderr
