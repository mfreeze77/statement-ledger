"""Explicit configuration precedence; credentials are resolved separately."""

from __future__ import annotations

import os
import re
import tomllib
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

ENV_FIELDS: dict[str, str] = {
    "SL_DATA_ROOT": "data_root",
    "SL_DB_PATH": "db_path",
    "SL_LEGACY_JOBS_PATH": "legacy_jobs_path",
    "SL_HOST": "host",
    "SL_PORT": "port",
    "SL_LOG_LEVEL": "log_level",
    "SL_ENABLE_JEV": "jev_enabled",
    "SL_JEV_MODEL": "jev_model",
    "SL_WORKER_CAPABILITY": "worker_capability",
    "SL_WORKER_POLL_SECONDS": "poll_seconds",
    "SL_WORKER_LEASE_SECONDS": "lease_seconds",
    "SL_WORKER_HEARTBEAT_SECONDS": "heartbeat_seconds",
    "SL_MAX_ARTIFACT_BYTES": "max_artifact_bytes",
    "SL_SQLITE_JOURNAL_MODE": "journal_mode",
    "SL_REMOTE_BUDGET_MICRO_USD": "remote_budget_micro_usd",
    "SL_REMOTE_ESTIMATE_MICRO_USD": "remote_estimate_micro_usd",
    "SL_SPEECH_MODEL_NAME": "speech_model_name",
    "SL_SPEECH_COMPUTE_TYPE": "speech_compute_type",
}
CONTROL_ENV = {"SL_CONFIG_FILE", "SL_ENV_FILE", "SL_SECRET_DIR", "SL_RUN_LIVE"}
SECRET_ALIASES: dict[str, tuple[str, ...]] = {
    "API_TOKEN": ("SL_API_TOKEN",),
    "TYPESAFE_API_KEY": ("TYPESAFE_API_KEY",),
    "YOUTUBE_API_KEY": ("YOUTUBE_API_KEY",),
    "FACTCHECK_API_KEY": ("FACTCHECK_API_KEY",),
    "HF_TOKEN": ("HF_TOKEN",),
}


class Settings(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    data_root: Path = Path("data")
    db_path: Path | None = None
    legacy_jobs_path: Path | None = None
    host: str = "127.0.0.1"
    port: int = Field(default=8765, ge=1, le=65535)
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    jev_enabled: bool = False
    jev_model: str = Field(default="jev-1.13.0", pattern=r"^jev-[a-zA-Z0-9_.-]+$")
    worker_capability: Literal["cpu", "gpu"] = "cpu"
    poll_seconds: float = Field(default=0.5, gt=0, le=60, allow_inf_nan=False)
    lease_seconds: int = Field(default=60, ge=3, le=3600)
    heartbeat_seconds: float = Field(default=10, gt=0, allow_inf_nan=False)
    max_artifact_bytes: int = Field(default=2_147_483_648, ge=1024)
    journal_mode: Literal["DELETE", "WAL"] = "DELETE"
    remote_budget_micro_usd: int = Field(default=0, ge=0)
    remote_estimate_micro_usd: int = Field(default=0, ge=0)

    speech_model_name: str = Field(default="whisper", pattern=r"^[a-zA-Z0-9_-]{1,80}$")
    speech_compute_type: Literal["float16", "int8_float16", "float32"] = "float16"

    @model_validator(mode="after")
    def check_lease(self) -> Settings:
        if self.heartbeat_seconds * 2 >= self.lease_seconds:
            raise ValueError("Heartbeat must be less than half the lease duration")
        return self

    @property
    def database(self) -> Path:
        return self.db_path or self.data_root / "db" / "ledger.sqlite3"

    @property
    def artifacts(self) -> Path:
        return self.data_root / "artifacts"

    def execution_hash(self) -> str:
        from statement_ledger.core.util import digest

        return str(
            digest(
                self.model_dump(
                    mode="json",
                    exclude={
                        "data_root",
                        "db_path",
                        "legacy_jobs_path",
                        "host",
                        "port",
                        "log_level",
                        "poll_seconds",
                        "lease_seconds",
                        "heartbeat_seconds",
                        "journal_mode",
                        "worker_capability",
                    },
                )
            )
        )

    def prepare_directories(self) -> None:
        # No database creation and no downloads; safe for an offline doctor command.
        for relative in (
            "db",
            "artifacts",
            "raw",
            "media",
            "models",
            "evaluation",
            "scratch",
            "backups",
        ):
            (self.data_root / relative).mkdir(parents=True, exist_ok=True)


def read_dotenv(path: Path | None) -> dict[str, str]:
    """Literal dotenv subset: KEY=value, optional quotes, no interpolation or execution."""
    if path is None:
        return {}
    result: dict[str, str] = {}
    for number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()
        key, sep, value = line.partition("=")
        key = key.strip()
        if not sep or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key) or key in result:
            raise ValueError(f"Invalid or duplicate dotenv key on line {number}")
        value = value.strip()
        if value.startswith(("'", '"')):
            if len(value) < 2 or value[-1] != value[0]:
                raise ValueError(f"Unclosed dotenv quote on line {number}")
            value = value[1:-1]
        elif " #" in value:
            value = value.split(" #", 1)[0].rstrip()
        result[key] = value
    return result


def environment(
    env_file: Path | None = None, environ: Mapping[str, str] | None = None
) -> dict[str, str]:
    process = dict(os.environ if environ is None else environ)
    selected = env_file or (Path(process["SL_ENV_FILE"]) if process.get("SL_ENV_FILE") else None)
    return {**read_dotenv(selected), **process}


def load_settings(
    *,
    config_file: Path | None = None,
    env_file: Path | None = None,
    environ: Mapping[str, str] | None = None,
    overrides: Mapping[str, Any] | None = None,
) -> Settings:
    env = environment(env_file, environ)
    config_file = config_file or (
        Path(env["SL_CONFIG_FILE"]) if env.get("SL_CONFIG_FILE") else None
    )
    values: dict[str, Any] = {}
    if config_file is not None:
        document = tomllib.loads(config_file.read_text(encoding="utf-8"))
        if set(document) - {"statement_ledger"}:
            raise ValueError("Only the statement_ledger TOML table is supported")
        values = dict(document.get("statement_ledger", {}))
        # File paths are relative to their config file; env/CLI paths are relative to cwd.
        for field in ("data_root", "db_path", "legacy_jobs_path"):
            if values.get(field) is not None:
                path = Path(values[field])
                values[field] = path if path.is_absolute() else config_file.resolve().parent / path
    for key, value in env.items():
        if key in ENV_FIELDS:
            values[ENV_FIELDS[key]] = value
        elif key.startswith("SL_") and not (
            key.startswith("SL_SECRET_")
            or key in CONTROL_ENV
            or any(key in aliases for aliases in SECRET_ALIASES.values())
        ):
            raise ValueError(f"Unknown application environment setting: {key}")
    values.update(overrides or {})
    try:
        result = Settings.model_validate(values)
    except ValidationError as exc:
        # Values may contain a mistakenly pasted credential. Never echo them.
        fields = sorted(
            {".".join(map(str, error["loc"])) for error in exc.errors(include_input=False)}
        )
        raise ValueError("Invalid application configuration fields: " + ", ".join(fields)) from None
    return result.model_copy(
        update={
            "data_root": result.data_root.resolve(),
            "db_path": result.db_path.resolve() if result.db_path else None,
        }
    )
