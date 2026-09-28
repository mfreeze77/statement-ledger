"""Deterministic planning only: no automatic crawl or external side effects."""
from .connectors.registry import sources

def plan_person(name: str,aliases: list[str] | None=None) -> dict:
    names = list(dict.fromkeys([name]+(aliases or [])))
    if not name.strip():
        raise ValueError("Person name is required")
    work=[]
    for source in sources():
        # Evidence is retrieved from a proposition's scope, never by searching the subject's name.
        if source["role"]=="primary_evidence":
            state="claim_driven"
        else:
            state="ready_to_configure" if source["implementation"] in {"http_client","file_parser"} else "access_or_adapter_required"
        work.append({"source_id":source["id"],"source_role":source["role"],"access":source["access"],
                     "implementation":source["implementation"],"queries":[] if state=="claim_driven" else names,
                     "state":state,
                     "next_step":source["next_step"],"cost_budget_required":True})
    return {"subject":name,"work":work,"strategies":["person_name","program_inventory","quotation_backtracking","source_link_following"],
            "automatic_execution":False,"completeness":"bounded discovered coverage only"}
