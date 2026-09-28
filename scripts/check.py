"""The mandatory check implementation shared by containers, CI, and local uv."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(*command: str) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["test", "check", "format", "contracts", "proof"])
    args = parser.parse_args()
    python = sys.executable
    if args.action == "format":
        run("ruff", "check", "--fix", ".")
        run("ruff", "format", ".")
        return 0
    if args.action in {"check", "contracts"}:
        if args.action == "check":
            run("uv", "lock", "--check", "--offline")
            run("ruff", "check", ".")
            run("ruff", "format", "--check", ".")
            run("mypy")
            run(python, "scripts/check-boundaries.py")
            run(python, "scripts/generate-environment.py", "--check")
            run(python, "scripts/check-standalone.py")
        run(python, "scripts/export-contracts.py")
        run(python, "scripts/compile-spec.py")
        run("git", "diff", "--exit-code", "--", "contracts", "SPECIFICATION.md")
    if args.action in {"test", "check"}:
        run(python, "-m", "pytest", "-q")
    if args.action in {"check", "proof"}:
        run(python, "scripts/foundation-proof.py")
    print(f"FOUNDATION_{args.action.upper()}_COMPLETE", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
