"""Operator-provisioned model manifests. No model acquisition or network access."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Any


def model_manifest(root: Path, expected_hash: str, *, verify_files: bool = False) -> dict[str, Any]:
    root = root.absolute()
    manifest = root / "manifest.json"
    if root.is_symlink() or manifest.is_symlink() or not manifest.is_file():
        raise ValueError("Provision an immutable local model directory and manifest first")
    raw = manifest.read_bytes()
    if len(raw) > 1024 * 1024 or hashlib.sha256(raw).hexdigest() != expected_hash:
        raise ValueError("Local model manifest changed or exceeds the size limit")
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("Model manifest must be an object")
    if (
        set(data) != {"format", "engine", "revision", "files"}
        or data["format"] != 1
        or data["engine"] != "faster-whisper"
    ):
        raise ValueError("Unsupported local model manifest")
    if (
        not isinstance(data["revision"], str)
        or not data["revision"].strip()
        or not isinstance(data["files"], dict)
        or not data["files"]
    ):
        raise ValueError("Local model manifest requires a revision and file checksums")
    if "model.bin" not in data["files"]:
        raise ValueError("CTranslate2 model.bin is required")
    for name, checksum in data["files"].items():
        relative = PurePosixPath(name)
        if relative.is_absolute() or ".." in relative.parts or "\\" in name or not relative.parts:
            raise ValueError("Unsafe model file key")
        path = root.joinpath(*relative.parts)
        if any(value.is_symlink() for value in [path, *path.parents] if value != root.parent):
            raise ValueError("Model files cannot traverse symlinks")
        if not path.is_file() or not isinstance(checksum, str) or len(checksum) != 64:
            raise ValueError("Invalid model file or checksum")
        if verify_files:
            digest = hashlib.sha256()
            with path.open("rb") as source:
                while chunk := source.read(1024 * 1024):
                    digest.update(chunk)
            if digest.hexdigest() != checksum:
                raise ValueError("Model weight checksum mismatch")
    return data


def transcribe_provisioned(path: Path, model_directory: Path, compute_type: str) -> dict[str, Any]:
    # The GPU image also sets HF_HUB_OFFLINE=1. Only pre-provisioned files are accepted.
    from faster_whisper import WhisperModel

    model = WhisperModel(
        str(model_directory), device="cuda", compute_type=compute_type, local_files_only=True
    )
    segments, info = model.transcribe(str(path), vad_filter=True, word_timestamps=True)
    return {
        "engine": "faster-whisper",
        "language": info.language,
        "segments": [
            {
                "start": segment.start,
                "end": segment.end,
                "text": segment.text,
                "speaker": "unassigned",
                "words": [
                    {
                        "start": word.start,
                        "end": word.end,
                        "word": word.word,
                        "probability": word.probability,
                    }
                    for word in (segment.words or [])
                ],
            }
            for segment in segments
        ],
    }
