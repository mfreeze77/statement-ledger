"""Static module ownership gate, including a deliberately forbidden-import self-test."""

from __future__ import annotations

import ast
import sys
from importlib.util import resolve_name
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "src"
OWNERS = {"contracts", "core", "infrastructure", "application", "pillars"}


def forbidden(source: str, target: str) -> bool:
    left, right = source.split("."), target.split(".")
    if len(left) < 2 or len(right) < 2 or right[0] != "statement_ledger":
        return False
    owner, other = left[1], right[1]
    if owner not in OWNERS:
        return False  # Root modules are compatibility facades, never new feature code.
    if other not in OWNERS:
        return True  # No new owner may import a legacy facade to evade boundaries.
    if owner == "contracts":
        return other != "contracts"
    if owner == "core":
        return other not in {"contracts", "core"}
    if owner == "infrastructure":
        return other not in {"contracts", "core", "infrastructure"}
    if owner == "pillars":
        return other == "application" or (
            other == "pillars" and len(right) > 2 and len(left) > 2 and left[2] != right[2]
        )
    return False  # Explicit composition root.


def check(root: Path = ROOT) -> list[str]:
    errors = []
    for path in sorted((root / "statement_ledger").rglob("*.py")):
        module = ".".join(path.relative_to(root).with_suffix("").parts)
        package = module.rsplit(".", 1)[0]
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            targets = []
            if isinstance(node, ast.Import):
                targets = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                name = "." * node.level + (node.module or "")
                target = resolve_name(name, package) if node.level else name
                # Include imported names: root compatibility aliases must not
                # provide a back door around owner boundaries.
                targets = [target] + [
                    target + "." + alias.name for alias in node.names if alias.name != "*"
                ]
            for target in targets:
                if forbidden(module, target):
                    errors.append(f"{path.relative_to(root)}:{node.lineno}: {target}")
    return errors


if __name__ == "__main__":
    assert forbidden(
        "statement_ledger.pillars.claims.library", "statement_ledger.pillars.speech.profiles"
    )
    assert forbidden("statement_ledger.core.ledger", "statement_ledger.application.ledger")
    assert forbidden("statement_ledger.pillars.claims.library", "statement_ledger.speech")
    assert not forbidden(
        "statement_ledger.application.ledger", "statement_ledger.pillars.speech.validators"
    )
    errors = check()
    print("\n".join(errors) if errors else "Module ownership boundaries passed")
    sys.exit(bool(errors))
