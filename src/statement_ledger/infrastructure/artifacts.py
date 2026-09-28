"""Immutable content-addressed local artifacts; keys are never trusted filesystem paths."""

from __future__ import annotations

import hashlib
import io
import os
import re
import shutil
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import BinaryIO, Protocol


@dataclass(frozen=True)
class Artifact:
    key: str
    sha256: str
    size: int

    def as_dict(self) -> dict[str, str | int]:
        return asdict(self)


class ArtifactStore(Protocol):
    def put(self, stream: BinaryIO, *, max_bytes: int | None = None) -> Artifact: ...
    def open(self, key: str) -> BinaryIO: ...
    def verify(self, artifact: Artifact) -> None: ...


class LocalArtifactStore:
    def __init__(self, root: Path, *, max_bytes: int = 2_147_483_648, readonly: bool = False):
        self.readonly = readonly
        if not readonly:
            root.mkdir(parents=True, exist_ok=True)
        if root.is_symlink():
            raise ValueError("Artifact root cannot be a symlink")
        self.root = root.resolve(strict=True)
        self.max_bytes = max_bytes
        self._temp = self.root / ".staging"
        if self._temp.is_symlink():
            raise ValueError("Artifact staging path cannot be a symlink")
        if not readonly:
            self._temp.mkdir(exist_ok=True)

    def _path(self, key: str) -> Path:
        if not re.fullmatch(r"sha256/[a-f0-9]{2}/[a-f0-9]{64}", key):
            raise ValueError("Invalid artifact key")
        parts = key.split("/")
        if parts[1] != parts[2][:2]:
            raise ValueError("Artifact shard/hash mismatch")
        candidate = self.root
        for part in parts:
            candidate = candidate / part
            if candidate.is_symlink():
                raise ValueError("Artifact symlinks are forbidden")
        if not candidate.resolve().is_relative_to(self.root):
            raise ValueError("Artifact escaped storage root")
        return candidate

    def put(self, stream: BinaryIO, *, max_bytes: int | None = None) -> Artifact:
        if self.readonly:
            raise ValueError("Artifact store is read-only")
        limit = min(self.max_bytes, max_bytes if max_bytes is not None else self.max_bytes)
        if limit < 0:
            raise ValueError("Invalid artifact byte limit")
        descriptor, name = tempfile.mkstemp(dir=self._temp)
        temp = Path(name)
        size = 0
        fingerprint = hashlib.sha256()
        try:
            with os.fdopen(descriptor, "wb") as output:
                while block := stream.read(1024 * 1024):
                    size += len(block)
                    if size > limit:
                        raise ValueError("Artifact exceeds byte limit")
                    fingerprint.update(block)
                    output.write(block)
                output.flush()
                os.fsync(output.fileno())
            checksum = fingerprint.hexdigest()
            key = f"sha256/{checksum[:2]}/{checksum}"
            destination = self._path(key)
            destination.parent.mkdir(parents=True, exist_ok=True)
            self._path(key)  # Recheck after directory creation.
            try:
                os.link(temp, destination)  # Atomic, no overwrite; same local filesystem.
            except FileExistsError:
                pass
            artifact = Artifact(key, checksum, size)
            self.verify(artifact)
            # Persist the directory entry before a database transaction references it.
            if os.name == "posix":
                directory = os.open(destination.parent, os.O_RDONLY)
                try:
                    os.fsync(directory)
                finally:
                    os.close(directory)
            return artifact
        finally:
            temp.unlink(missing_ok=True)

    def put_bytes(self, body: bytes) -> Artifact:
        return self.put(io.BytesIO(body))

    def open(self, key: str) -> BinaryIO:
        path = self._path(key)
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(path, flags)
        return os.fdopen(descriptor, "rb")

    def verify(self, artifact: Artifact) -> None:
        fingerprint = hashlib.sha256()
        size = 0
        with self.open(artifact.key) as source:
            while block := source.read(1024 * 1024):
                fingerprint.update(block)
                size += len(block)
        if (
            fingerprint.hexdigest() != artifact.sha256
            or size != artifact.size
            or artifact.key.rsplit("/", 1)[-1] != artifact.sha256
        ):
            raise ValueError("Artifact integrity check failed")

    @contextmanager
    def materialize(self, artifact: Artifact, *, suffix: str = "") -> Iterator[Path]:
        if not re.fullmatch(r"(?:\.[a-zA-Z0-9]{1,10})?", suffix):
            raise ValueError("Invalid artifact suffix")
        self.verify(artifact)
        with tempfile.TemporaryDirectory(dir=self._temp) as name:
            path = Path(name) / ("input" + suffix)
            with self.open(artifact.key) as source, path.open("wb") as output:
                shutil.copyfileobj(source, output)
            yield path

    def inspect_orphans(self, referenced_keys: set[str]) -> dict[str, list[str]]:
        present = {
            str(path.relative_to(self.root))
            for path in self.root.glob("sha256/*/*")
            if path.is_file() and not path.is_symlink()
        }
        return {
            "unreferenced": sorted(present - referenced_keys),
            "missing": sorted(referenced_keys - present),
            "staging": sorted(path.name for path in self._temp.iterdir()),
        }
