"""Cross-record invariants for derived acceleration artifacts."""
from __future__ import annotations
from datetime import datetime
from .policy import PolicyError
from .util import digest

def validate_extension(ledger,kind,p,ref):
    if kind=="speaker_profile":
        from .profiles import derive_profile
        ref("person",p["person_id"])
        for uid in p["example_ids"]+p["background_ids"]:ref("utterance",uid)
        expected=derive_profile(ledger,p["person_id"],p["example_ids"],p["background_ids"],p["config"])
        if {k:v for k,v in p.items() if k!="id"}!=expected:raise PolicyError("Profile must be reproducibly derived from accepted source turns")
    elif kind=="localization_run":
        from .localization import derive_localization
        ref("speaker_profile",p["profile_id"]);ref("transcript",p["transcript_id"]);ref("asset",p["asset_id"])
        for rid in p["decision_run_ids"]:ref("decision_run",rid)
        for b in p["bindings"]:
            ref(b["kind"],b["id"])
            if ledger.store.get(b["kind"],b["id"])["revision"]!=b["revision"]:raise PolicyError("Localization dependency changed")
        expected=derive_localization(ledger,p["profile_id"],p["transcript_id"],p["config"],p["decision_run_ids"])
        if {k:v for k,v in p.items() if k!="id"}!=expected:raise PolicyError("Localization output must match its source/configuration")
    elif kind=="decision_run":
        from .jev import validate_questions, validate_response
        validate_questions(p["questions"])
        for b in p["bindings"]:
            ref(b["kind"],b["id"])
            if ledger.store.get(b["kind"],b["id"])["revision"]!=b["revision"]:raise PolicyError("Decision binding revision mismatch")
        for rid in p["receipt_ids"]:
            receipt=ledger.store.provider_receipt(rid)
            if receipt["request_hash"]!=p["request_hash"]:raise PolicyError("Provider receipt request mismatch")
            meta=receipt["request_metadata"]
            if meta["model"]!=p["model_requested"] or meta["purpose"]!=p["purpose"] or meta["question_version"]!=p["question_version"] or digest(meta)!=p["request_hash"] or meta["bindings"]!=p["bindings"] or meta["questions"]!=p["questions"] or meta["input_ids"]!=p["input_ids"] or digest(meta["state"])!=p["state_sha256"]:
                raise PolicyError("Provider receipt binding mismatch")
        if p["status"]=="available":
            if not p["receipt_ids"]:raise PolicyError("Available decision requires a captured provider response")
            from .jev import strict_loads
            receipt=ledger.store.provider_receipt(p["receipt_ids"][-1])
            if receipt["http_status"]!=200 or receipt["truncated"]:raise PolicyError("Available decision needs an intact HTTP 200 receipt")
            validated=validate_response(strict_loads(receipt["body"]),p["questions"],p["model_requested"])
            if p["answers"]!=validated["answers"] or p["warnings"]!=validated["warnings"] or p["model_resolved"]!=validated["model_resolved"] or p["usage"]!=validated["usage"]:
                raise PolicyError("Decision differs from its captured response")
    elif kind=="claim_family":
        if len(set(p["proposition_ids"]))!=len(p["proposition_ids"]):raise PolicyError("Family members must be unique")
        for rid in p["proposition_ids"]:ref("proposition",rid)
    elif kind=="claim_card":
        prop=ref("proposition",p["proposition_id"])
        if len(set(p["review_ids"]))!=len(p["review_ids"]):raise PolicyError("Card reviews must be unique")
        for rid in p["review_ids"]:
            review=ref("review",rid)
            if review["status"]!="reviewed" or review["proposition_id"]!=p["proposition_id"]:
                raise PolicyError("Claim card requires reviewed findings for this exact proposition")
            if datetime.fromisoformat(p["valid_until"])<=datetime.fromisoformat(review["reviewed_at"]):
                raise PolicyError("Card expiry must follow its review dates")
