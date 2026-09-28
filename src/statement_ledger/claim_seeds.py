"""Bounded bulk seed interchange: retain source leads without importing their verdicts."""
from __future__ import annotations
from pathlib import Path
from pydantic import Field
from .models import Model,Text,Scope,ID,RightsGrant
from .policy import require_right
from .profiles import current
from .store import Missing
from .util import digest
from .ingest import archive_file
from .connectors.parsers import iter_rows

class ClaimSeed(Model):
    native_id: Text
    source_url: Text
    claim_text: Text
    scope: Scope=Field(default_factory=Scope)
    attributed_to: str | None=None


def import_claim_seeds(ledger,path:Path,source_id,rights_id,*,archive_root:Path,max_records=10000,actor="local-operator"):
    """Explicitly transformed claim text, not an arbitrary full article or an LLM verdict.

One row requires native_id, source_url and claim_text. Findings and truth labels
are deliberately not accepted. Every source needs an authorized preprocessing step.
"""
    grant=RightsGrant.model_validate(current(ledger,"rights",rights_id)["payload"])
    require_right(grant,"store_text",source_id)
    if not 1<=max_records<=1_000_000:raise ValueError("max_records must be 1..1000000")
    sha,stored=archive_file(path,archive_root)
    # iter_rows accepts compression by suffix; retain a sidecar hard-link where needed.
    suffix=path.suffix if path.suffix in {".gz",".bz2"} else ""
    parse_path=stored
    if suffix:
        import os,shutil
        parse_path=stored.with_name(stored.name+suffix)
        if not parse_path.exists():
            try:os.link(stored,parse_path)
            except OSError:shutil.copyfile(stored,parse_path)
    result={"format":"claim-seeds-v1","source_id":source_id,"file_sha256":sha,"archive_path":str(stored),
        "rows_read":0,"created_propositions":0,"unchanged_propositions":0,"errors":[],"findings_created":0,
        "completion":"unknown","max_records":max_records}
    try:
        for line,row in enumerate(iter_rows(parse_path,max_records=max_records),1):
            result["rows_read"]+=1
            try:
                seed=ClaimSeed.model_validate(row)
                oid="seed-source-"+digest([source_id,seed.native_id,row])[:32]
                try:current(ledger,"observation",oid)
                except Missing:
                    ledger.put("observation",{"id":oid,"source_id":source_id,"native_id":seed.native_id,
                        "rights_id":rights_id,"kind":"quotation_lead","url":seed.source_url,"text":seed.claim_text,
                        "reported_speaker":seed.attributed_to,"raw_payload":row,"raw_sha256":digest(row)},actor=actor)
                # Exact text and complete stored scope only; no paraphrase auto-merge.
                pid="seed-claim-"+digest([seed.claim_text,seed.scope.model_dump()])[:32]
                try:
                    old=current(ledger,"proposition",pid)
                    p=old["payload"]
                    if oid not in p.get("seed_observation_ids",[]):
                        ledger.put("proposition",{**p,"seed_observation_ids":[*p.get("seed_observation_ids",[]),oid]},old["revision"],actor)
                    result["unchanged_propositions"]+=1
                except Missing:
                    ledger.put("proposition",{"id":pid,"text":seed.claim_text,"kind":"ambiguous","scope":seed.scope.model_dump(),"seed_observation_ids":[oid]},actor=actor)
                    result["created_propositions"]+=1
            except (ValueError,KeyError) as exc:
                result["errors"].append({"line":line,"error_type":type(exc).__name__,"message":str(exc)[:300]})
        result["completion"]="bounded_or_eof" if result["rows_read"]>=max_records else "eof"
    except (ValueError,UnicodeError,EOFError,OSError) as exc:
        result["errors"].append({"line":result["rows_read"]+1,"error_type":type(exc).__name__})
        result["completion"]="parse_failed_partial_commit"
    result["success"]=not result["errors"]
    return result
