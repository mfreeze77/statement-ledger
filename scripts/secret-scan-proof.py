"""Synthetic detection test; never uses or prints an actual credential."""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory() as name:
    root = Path(name)
    marker = "ghp_" + "X" * 36  # Constructed at runtime, not a committed token.
    (root / "sample.txt").write_text("token=" + marker + "\n", encoding="utf-8")
    result = subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "-v",
            f"{root}:/scan",
            "zricethezav/gitleaks:v8.24.2@sha256:b5918eb91b8d2473cec722f066abb4352e4ffdc4ec9f4283ec143aba9ec9ebc4",
            "dir",
            "/scan",
            "--redact",
            "--report-format",
            "json",
            "--report-path",
            "/scan/report.json",
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 1 or not (root / "report.json").exists():
        raise SystemExit("Synthetic secret detection failed")
    report = (root / "report.json").read_text()
    if marker in report or marker in result.stdout or marker in result.stderr:
        raise SystemExit("Secret scanning failed redaction")
    if not json.loads(report):
        raise SystemExit("Synthetic secret was not detected")
    print("Synthetic credential detected; report and logs redacted")
