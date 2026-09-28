"""Catch accidental coupling to another application's known namespaces."""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Fragmented to avoid falsely matching this guard itself.
forbidden = ["state" + "civics", "kansas" + "_accountability", "svs" + "_common", r"\bKS-\d+"]
paths = (
    list((ROOT / "src").rglob("*.py"))
    + list((ROOT / "config").glob("*"))
    + [ROOT / "compose.yaml", ROOT / "pyproject.toml"]
)
errors = []
for p in paths:
    if not p.is_file():
        continue
    text = p.read_text(encoding="utf-8")
    if any(re.search(x, text, re.I) for x in forbidden):
        errors.append(str(p.relative_to(ROOT)))
if errors:
    print("Unexpected external-project coupling:", *errors, sep="\n")
    sys.exit(1)
print("Standalone namespace/configuration guard passed.")
