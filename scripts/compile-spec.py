from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
chapters = sorted((ROOT / "docs/spec").glob("[0-9][0-9]_*.md"))
header = "# Statement Ledger — Complete Product and Engineering Specification\n\nSpecification 1.1 · Software 0.2.0 · 2026-09-27 · Standalone project\n\nThis file is generated from `docs/spec/`. Chapters 00–22 preserve the original design and historical v0.1 boundaries; chapters 23–28 and docs/IMPLEMENTATION_STATUS.md define this upgrade. Implementation status is explicit; target requirements are not claims of completed code.\n\n"
(ROOT / "SPECIFICATION.md").write_text(
    header + "\n\n---\n\n".join(p.read_text(encoding="utf-8") for p in chapters),
    encoding="utf-8",
    newline="\n",
)
