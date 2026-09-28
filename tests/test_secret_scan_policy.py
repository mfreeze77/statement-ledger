"""Review-specific exceptions and scanner failure handling must remain narrow."""

from __future__ import annotations

import hashlib
import json
import math
import re
import runpy
import subprocess
import tomllib
from collections import Counter
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PROOF = runpy.run_path(str(ROOT / "scripts/secret-scan-proof.py"))


def test_allowlisted_values_are_reproducible_event_ids():
    fixture = json.loads((ROOT / "proof/synthetic-demo.json").read_text(encoding="utf-8"))
    actual = set()
    for row in fixture["items"]:
        coordinates = [
            row["event_id"],
            fixture["person"]["id"],
            row["proposition_id"],
            row["event_start_ms"],
            row["event_end_ms"],
        ]
        encoded = json.dumps(coordinates, sort_keys=True, separators=(",", ":")).encode()
        expected = hashlib.sha256(encoded).hexdigest()
        assert row["canonical_key"] == expected
        actual.add(expected)
    assert len(actual) == 2
    policy = tomllib.loads((ROOT / ".gitleaks.toml").read_text())
    assert policy["extend"]["useDefault"] is True
    assert set(policy) == {"title", "extend", "rules"}
    assert len(policy["rules"]) == 1
    rule = policy["rules"][0]
    assert set(rule) == {"id", "allowlists"}
    assert rule["id"] == "generic-api-key"
    assert len(rule["allowlists"]) == 1
    exception = rule["allowlists"][0]
    assert exception["condition"] == "AND"
    assert exception["regexTarget"] == "line"
    assert not exception.get("commits")
    path_pattern = exception["paths"][0]
    line_pattern = exception["regexes"][0]
    assert re.search(path_pattern, "proof/synthetic-demo.json")
    assert not re.search(path_pattern, "proof/not-the-demo.json")
    for value in actual:
        assert re.search(line_pattern, f'  "canonical_key": "{value}",')
        assert not re.search(line_pattern, f'  "api_key": "{value}",')
        assert not re.search(line_pattern, f'  "canonical_key": "{value}", "token": "other"')
    changed = hashlib.sha256(b"unreviewed-value").hexdigest()
    assert not re.search(line_pattern, f'  "canonical_key": "{changed}",')


def test_synthetic_marker_exceeds_detector_entropy_floor():
    marker = PROOF["synthetic_marker"]()
    assert len(marker) == 40
    entropy = -sum(
        (count / len(marker)) * math.log2(count / len(marker)) for count in Counter(marker).values()
    )
    assert entropy > 3.0
    assert marker not in (ROOT / "scripts/secret-scan-proof.py").read_text()


@pytest.mark.parametrize(
    ("exit_code", "report", "stdout", "expected_rule"),
    [
        (125, [], "", None),
        (0, None, "", None),
        (0, "invalid-json", "", None),
        (0, {}, "", None),
        (1, [], "", "github-pat"),
        (1, [{"RuleID": "generic-api-key"}], "", "github-pat"),
        (0, [{"RuleID": "github-pat"}], "", None),
        (1, [{"RuleID": "github-pat"}], "LEAK", "github-pat"),
        (1, [{"RuleID": "github-pat", "Secret": "LEAK"}], "", "github-pat"),
    ],
)
def test_scan_validator_fails_closed(tmp_path, exit_code, report, stdout, expected_rule):
    path = tmp_path / "report.json"
    if report is not None:
        path.write_text(report if isinstance(report, str) else json.dumps(report))
    result = subprocess.CompletedProcess([], exit_code, stdout=stdout, stderr="")
    with pytest.raises(RuntimeError) as caught:
        PROOF["validate_scan"](result, path, case="test", expected_rule=expected_rule, marker="LEAK")
    assert "LEAK" not in str(caught.value)


@pytest.mark.parametrize("expected_rule", [None, "github-pat"])
def test_scan_validator_accepts_only_expected_outcome(tmp_path, expected_rule):
    findings = [] if expected_rule is None else [{"RuleID": expected_rule, "Secret": "REDACTED"}]
    path = tmp_path / "report.json"
    path.write_text(json.dumps(findings))
    result = subprocess.CompletedProcess([], 0 if expected_rule is None else 1, stdout="", stderr="")
    PROOF["validate_scan"](result, path, case="test", expected_rule=expected_rule, marker="LEAK")
