"""Exercise the pinned scanner and project policy without real credentials.

The old all-X marker did not meet the default GitHub-PAT rule's entropy floor.
Create a deterministic, sufficiently varied marker at runtime instead. Never
print it, call a provider with it, or commit it to the actual repository.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

IMAGE = (
    "zricethezav/gitleaks:v8.24.2@sha256:"
    "b5918eb91b8d2473cec722f066abb4352e4ffdc4ec9f4283ec143aba9ec9ebc4"
)


def synthetic_marker() -> str:
    """Return a non-issued marker; no live credential is read or generated."""
    suffix = hashlib.sha256(b"statement-ledger-secret-scan-self-test-v2").hexdigest()[:36]
    return "ghp_" + suffix


def validate_scan(
    result: subprocess.CompletedProcess[str],
    report_path: Path,
    *,
    case: str,
    expected_rule: str | None,
    marker: str,
) -> None:
    """Fail closed on backend errors, absent reports, missed leaks or redaction loss."""
    expected_code = 0 if expected_rule is None else 1
    if result.returncode != expected_code or not report_path.is_file():
        raise RuntimeError(f"{case}: scanner exit/report mismatch (exit={result.returncode})")
    raw_report = report_path.read_text(encoding="utf-8")
    if any(marker in value for value in (raw_report, result.stdout, result.stderr)):
        raise RuntimeError(f"{case}: scanner redaction failure")
    try:
        findings = json.loads(raw_report)
    except json.JSONDecodeError:
        raise RuntimeError(f"{case}: malformed scanner report") from None
    if not isinstance(findings, list) or any(not isinstance(row, dict) for row in findings):
        raise RuntimeError(f"{case}: invalid scanner report shape")
    if expected_rule is None and findings:
        raise RuntimeError(f"{case}: synthetic hash exception did not match")
    if expected_rule is not None and not any(
        row.get("RuleID") == expected_rule for row in findings
    ):
        raise RuntimeError(f"{case}: expected detector did not fire")


def main() -> None:
    repository = Path(__file__).resolve().parents[1]
    fixture = json.loads((repository / "proof/synthetic-demo.json").read_text(encoding="utf-8"))
    known_hash = fixture["items"][0]["canonical_key"]
    marker = synthetic_marker()
    different_hash = hashlib.sha256(b"not-a-reviewed-synthetic-canonical-id").hexdigest()
    # Positive controls deliberately live in the exempted path as well as elsewhere.
    cases = [
        ("reviewed-hashes", "proof/synthetic-demo.json", fixture, None),
        ("pat-same-path", "proof/synthetic-demo.json", {"token": marker}, "github-pat"),
        (
            "different-value",
            "proof/synthetic-demo.json",
            {"canonical_key": different_hash},
            "generic-api-key",
        ),
        (
            "different-path",
            "proof/not-the-demo.json",
            {"canonical_key": known_hash},
            "generic-api-key",
        ),
        (
            "different-field",
            "proof/synthetic-demo.json",
            {"api_key": known_hash},
            "generic-api-key",
        ),
    ]
    with tempfile.TemporaryDirectory(prefix="sl-secret-proof-") as name:
        root = Path(name)
        scan = root / "scan"
        reports = root / "reports"
        reports.mkdir()
        for case, relative_path, payload, expected_rule in cases:
            if scan.exists():
                shutil.rmtree(scan)
            target = scan / relative_path
            target.parent.mkdir(parents=True)
            target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            report = reports / f"{case}.json"
            result = subprocess.run(
                [
                    "docker",
                    "run",
                    "--rm",
                    "--network=none",
                    "-v",
                    f"{scan}:/scan:ro",
                    "-v",
                    f"{reports}:/reports",
                    "-v",
                    f"{repository / '.gitleaks.toml'}:/policy.toml:ro",
                    IMAGE,
                    "dir",
                    "/scan",
                    "--config",
                    "/policy.toml",
                    "--redact=100",
                    "--no-banner",
                    "--report-format",
                    "json",
                    "--report-path",
                    f"/reports/{case}.json",
                ],
                capture_output=True,
                text=True,
                timeout=120,
                check=False,
            )
            validate_scan(result, report, case=case, expected_rule=expected_rule, marker=marker)
            print(f"{case}: passed (report/log redaction verified)")
    print("Secret-scan proof passed: reviewed hashes only; all positive controls detected")


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, subprocess.TimeoutExpired) as error:
        # Never emit captured stdout/stderr or token-bearing subprocess arguments.
        message = str(error) if isinstance(error, RuntimeError) else type(error).__name__
        raise SystemExit(message) from None
