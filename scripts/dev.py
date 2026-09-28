"""Cross-platform Docker entrypoint. No local provider credential is needed for tests."""

from __future__ import annotations

import argparse
import os
import secrets
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(*args: str) -> None:
    subprocess.run(args, cwd=ROOT, check=True)


def bootstrap() -> None:
    env = ROOT / ".env"
    lines = env.read_text(encoding="utf-8").splitlines() if env.exists() else []
    aliases = ("SL_SECRET_API_TOKEN=", "SL_API_TOKEN=")
    if not any(
        line.startswith(aliases) and line.partition("=")[2].strip().strip("\"'") for line in lines
    ):
        lines = [line for line in lines if not line.startswith(aliases)]
        lines.append("SL_SECRET_API_TOKEN=" + secrets.token_urlsafe(48))
        env.write_text("\n".join(lines) + "\n", encoding="utf-8")
    if os.name != "nt":
        env.chmod(0o600)
    (ROOT / "local-models").mkdir(exist_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "action",
        choices=[
            "up",
            "down",
            "test",
            "check",
            "format",
            "contracts",
            "proof",
            "migrate",
            "doctor",
            "worker",
            "backup",
            "restore",
            "gpu",
            "logs",
            "cli",
        ],
    )
    parser.add_argument("arguments", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if not shutil.which("docker"):
        parser.error(
            "Docker Compose is required; use uv run --locked python scripts/check.py for native checks"
        )
    command = ["docker", "compose"]
    if args.action == "up":
        bootstrap()
        run(*command, "up", "--build", "-d", "api", "worker")
    elif args.action == "down":
        run(*command, "--profile", "gpu", "down")  # Deliberately never removes volumes.
    elif args.action == "gpu":
        bootstrap()
        run(*command, "--profile", "gpu", "up", "--build", "-d", "gpu-worker")
    elif args.action == "logs":
        run(*command, "logs", "--tail", "100", *args.arguments)
    elif args.action in {"test", "check", "format", "contracts", "proof"}:
        user = [] if os.name == "nt" else ["--user", f"{os.getuid()}:{os.getgid()}"]
        run(
            *command,
            "run",
            "--build",
            "--rm",
            "--no-deps",
            *user,
            "dev",
            "python",
            "scripts/check.py",
            args.action,
        )
    else:
        native = {"backup": "backup-workspace", "restore": "restore-workspace"}.get(
            args.action, args.action
        )
        parts = args.arguments if args.action == "cli" else [native, *args.arguments]
        run(*command, "run", "--build", "--rm", "--no-deps", "dev", "statement-ledger", *parts)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        raise SystemExit(exc.returncode) from None
