"""A green CI result must mean every required gate actually completed."""

from __future__ import annotations

import runpy
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_workflow_explicitly_enables_pipeline_failure_propagation():
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "defaults:\n  run:\n    shell: bash\n" in workflow
    assert "continue-on-error" not in workflow
    assert "scripts/check.py check 2>&1 | tee" in workflow
    assert "scripts/dev.py proof 2>&1 | tee" in workflow


@pytest.mark.skipif(shutil.which("bash") is None, reason="Container/CI uses Bash")
def test_logged_pipeline_preserves_failure_status(tmp_path):
    result = subprocess.run(
        [
            "bash",
            "--noprofile",
            "--norc",
            "-eo",
            "pipefail",
            "-c",
            "(printf 'synthetic-gate-failed\\n'; exit 23) 2>&1 | tee check.txt",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 23
    assert "synthetic-gate-failed" in (tmp_path / "check.txt").read_text()


def test_runner_does_not_report_completion_after_a_failed_gate(monkeypatch, capsys):
    main = runpy.run_path(str(ROOT / "scripts/check.py"))["main"]
    calls = []

    def fail_gate(*command):
        calls.append(command)
        if command[0] == "ruff":
            raise subprocess.CalledProcessError(23, command)

    monkeypatch.setitem(main.__globals__, "run", fail_gate)
    monkeypatch.setattr(sys, "argv", ["check.py", "check"])
    with pytest.raises(subprocess.CalledProcessError):
        main()
    assert len(calls) == 2
    assert "FOUNDATION_CHECK_COMPLETE" not in capsys.readouterr().out


def test_runner_reports_completion_only_after_all_gates(monkeypatch, capsys):
    main = runpy.run_path(str(ROOT / "scripts/check.py"))["main"]
    calls = []
    monkeypatch.setitem(main.__globals__, "run", lambda *command: calls.append(command))
    monkeypatch.setattr(sys, "argv", ["check.py", "check"])
    assert main() == 0
    assert calls[-1][-1] == "scripts/foundation-proof.py"
    assert "FOUNDATION_CHECK_COMPLETE" in capsys.readouterr().out
