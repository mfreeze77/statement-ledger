"""Repeatable integrated proof. Default execution leaves no operator data behind."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from statement_ledger.application.proof import prove  # noqa: E402

parser = argparse.ArgumentParser()
parser.add_argument("--workspace", type=Path)
args = parser.parse_args()
if args.workspace:
    result = prove(args.workspace)
else:
    with tempfile.TemporaryDirectory(prefix="statement-ledger-foundation-") as name:
        result = prove(Path(name) / "workspace")
print(json.dumps(result, indent=2, sort_keys=True))
