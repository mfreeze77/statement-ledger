import bz2
import gzip
import hashlib
import json
import os
import tempfile
from collections.abc import Iterator
from pathlib import Path
from typing import Any

MAX_LINE = 8 * 1024 * 1024


class ParseError(ValueError):
    pass


def open_text(path: Path):
    if path.suffix == ".gz":
        return gzip.open(path, "rt", encoding="utf-8-sig")
    if path.suffix == ".bz2":
        return bz2.open(path, "rt", encoding="utf-8-sig")
    return path.open("rt", encoding="utf-8-sig")


def iter_rows(
    path: Path,
    *,
    max_records: int = 100_000,
    max_line: int = MAX_LINE,
    max_json_bytes: int = 64 * 1024 * 1024,
) -> Iterator[dict]:
    if max_records < 1 or max_line < 1 or max_json_bytes < 1:
        raise ValueError("Input bounds must be positive")
    with open_text(path) as f:
        first = f.read(1)
        while first and first.isspace():
            first = f.read(1)
        if not first:
            return
        if first == "[":
            # Explicit bounded array import; never json.load an unbounded corpus.
            tail = f.read(max_json_bytes + 1)
            if len(tail.encode("utf-8")) > max_json_bytes:
                raise ParseError("JSON array exceeds configured bound; convert to JSONL")
            try:
                data = json.loads("[" + tail)
            except json.JSONDecodeError as e:
                raise ParseError("Invalid JSON array") from e
            if not isinstance(data, list):
                raise ParseError("Expected array")
            for row in data[:max_records]:
                if not isinstance(row, dict):
                    raise ParseError("Every row must be an object")
                yield row
            return
        # JSONL supports objects only; pretty-printed single objects use .json mode
        # via read_document instead. This prevents unbounded buffering ambiguity.
        prefix = first
        for number in range(1, max_records + 1):
            line = prefix + f.readline(max_line + 1)
            prefix = ""
            if not line:
                return
            if len(line.encode("utf-8")) > max_line:
                raise ParseError(f"Line {number} exceeds limit")
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as e:
                raise ParseError(f"Invalid JSONL at physical line {number}") from e
            if not isinstance(row, dict):
                raise ParseError(f"Line {number} is not an object")
            yield row


def read_document(path: Path, max_bytes: int = 64 * 1024 * 1024) -> Any:
    with open_text(path) as f:
        value = f.read(max_bytes + 1)
    if len(value.encode("utf-8")) > max_bytes:
        raise ParseError("Document exceeds bound")
    return json.loads(value)


def archive_file(path: Path, archive_root: Path) -> tuple[str, Path]:
    archive_root.mkdir(parents=True, exist_ok=True)
    h = hashlib.sha256()
    # Hash the same bytes that are retained, not a race-prone second read.
    fd, name = tempfile.mkstemp(prefix="incoming-", dir=archive_root)
    tmp = Path(name)
    try:
        with os.fdopen(fd, "wb") as out, path.open("rb") as inp:
            while chunk := inp.read(1024 * 1024):
                h.update(chunk)
                out.write(chunk)
            out.flush()
            os.fsync(out.fileno())
        dest = archive_root / h.hexdigest()
        if dest.exists():
            tmp.unlink()
        else:
            os.replace(tmp, dest)
        return h.hexdigest(), dest
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise
