"""Named credentials. Neither configuration nor domain records contain secret values."""

from __future__ import annotations

import re
from collections.abc import Mapping
from pathlib import Path
from typing import Protocol

from pydantic import SecretStr

from .settings import SECRET_ALIASES, environment


class SecretResolver(Protocol):
    def resolve(self, name: str, *, required: bool = True) -> SecretStr | None: ...


class LocalSecrets:
    def __init__(
        self,
        *,
        environ: Mapping[str, str] | None = None,
        env_file: Path | None = None,
        directory: Path | None = None,
    ):
        self._env = environment(env_file, environ)
        self._directory = directory or (
            Path(self._env["SL_SECRET_DIR"]) if self._env.get("SL_SECRET_DIR") else None
        )

    def resolve(self, name: str, *, required: bool = True) -> SecretStr | None:
        if not re.fullmatch(r"[A-Z][A-Z0-9_]{0,99}", name):
            raise ValueError("Invalid credential reference")
        canonical = "SL_SECRET_" + name
        values = [
            self._env[key]
            for key in (canonical, *SECRET_ALIASES.get(name, ()))
            if self._env.get(key)
        ]
        if self._directory is not None:
            root = self._directory.resolve(strict=True)
            file = root / canonical
            if file.is_symlink():
                raise ValueError("Secret-file symlinks are not accepted")
            if file.is_file():
                if file.stat().st_size > 65536:
                    raise ValueError("Secret file exceeds size limit")
                values.append(file.read_text(encoding="utf-8").rstrip("\r\n"))
        if len(set(values)) > 1:
            raise ValueError(f"Conflicting values for credential reference {name}")
        if not values or not values[0]:
            if required:
                raise RuntimeError(f"Credential reference {name} is not configured")
            return None
        return SecretStr(values[0])

    def value(self, name: str, *, required: bool = True) -> str:
        secret = self.resolve(name, required=required)
        return secret.get_secret_value() if secret is not None else ""
