from importlib.resources import files
import json

def sources() -> list[dict]:
    return json.loads(files("statement_ledger").joinpath("sources.json").read_text(encoding="utf-8"))

def source(source_id: str) -> dict:
    for item in sources():
        if item["id"] == source_id:
            return item
    raise ValueError(f"Unknown source: {source_id}")
