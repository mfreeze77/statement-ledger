"""Hash already provisioned CTranslate2 files. Does not acquire weights or accept licenses."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("directory", type=Path)
parser.add_argument("--revision", required=True)
parser.add_argument("--confirm-rights", action="store_true", required=True)
args = parser.parse_args()
if not args.directory.is_dir() or not (args.directory / "model.bin").is_file():
    parser.error("Provide an existing, authorized faster-whisper/CTranslate2 model directory")
files = {}
for path in sorted(args.directory.rglob("*")):
    if path.is_symlink():
        parser.error("Model symlinks are not accepted")
    if path.is_file() and path.name != "manifest.json":
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            while block := stream.read(1024 * 1024):
                digest.update(block)
        files[path.relative_to(args.directory).as_posix()] = digest.hexdigest()
raw = (
    json.dumps(
        {"format": 1, "engine": "faster-whisper", "revision": args.revision, "files": files},
        sort_keys=True,
        indent=2,
    ).encode()
    + b"\n"
)
manifest = args.directory / "manifest.json"
if manifest.exists() and manifest.read_bytes() != raw:
    parser.error("Manifest exists with different content; use a new versioned model directory")
manifest.write_bytes(raw)
print(
    json.dumps(
        {
            "model_manifest_sha256": hashlib.sha256(raw).hexdigest(),
            "files": len(files),
            "downloads": False,
        }
    )
)
