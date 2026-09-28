"""Deterministic synthetic corpus. No statements attributed to a real person."""
from .util import digest
from .store import Missing

PERSON_ID="synthetic-dana-example"
SCOPE={"entity":"Synthetic Lab","metric":"samples processed","geography":"fictional facility",
       "period":"2025","unit":"samples","baseline":"not_applicable","comparator":"equals",
       "quantity":"200","definition":"completed samples in synthetic log"}

def seed(ledger, *, expanded=False):
    scope={**SCOPE,**({"polarity":"affirmative","conditions":"not_applicable","population":"synthetic samples","accounting_basis":"not_applicable","document_version":"fixture-v1"} if expanded else {})}
    if ledger.store.counts():
        try:
            row=ledger.store.get("person",PERSON_ID)
            if row["payload"]["synthetic"]:return ledger.person_ledger(PERSON_ID)
        except Missing:pass
        raise ValueError("Demo seed requires an empty database; never mix synthetic data into a real workspace")
    def write(kind,p):return ledger.put(kind,p,actor="synthetic-fixture")
    write("person",{"id":PERSON_ID,"display_name":"Dana Example (synthetic)","synthetic":True})
    write("rights",{"id":"demo-rights","source_id":"manual_import","basis":"Project-created synthetic records only",
        "allowed":["discover","store_text","store_media","process_audio","derive_clip"]+(["learn_profile","send_to_provider","process_biometrics"] if expanded else []),"reviewed_by":"synthetic-fixture"})
    source_records=[("demo-show","Synthetic appearance; recorded on 2025-05-01."),
                    ("demo-repeat","Another synthetic appearance; recorded on 2025-05-02."),
                    ("demo-evidence","Synthetic Lab processed 100 completed samples in 2025.")]
    for ident,text in source_records:
        raw={"id":ident,"text":text,"synthetic":True}
        write("observation",{"id":ident,"source_id":"manual_import","native_id":ident,"rights_id":"demo-rights",
             "kind":"primary_document" if ident=="demo-evidence" else "appearance_lead",
             "url":f"https://example.org/{ident}","text":text,"title":ident,"raw_payload":raw,"raw_sha256":digest(raw)})
    for eid,oid,day in (("event-1","demo-show","2025-05-01"),("event-2","demo-repeat","2025-05-02")):
        write("event",{"id":eid,"title":"Synthetic interview","occurred_at":day,"date_precision":"day",
             "date_evidence":"Explicit synthetic fixture date","observation_ids":[oid],"synthetic":True})
        write("appearance",{"id":f"appearance-{eid}","event_id":eid,"person_id":PERSON_ID,"observation_ids":[oid],
             "status":"confirmed","reviewer":"synthetic-fixture","rationale":"Synthetic known identity; not biometric inference"})
    write("proposition",{"id":"proposition-1","text":"Synthetic Lab processed 200 samples in 2025.","scope":scope})
    for aid,eid,oid,start,end,offset,role in (
        ("asset-original","event-1","demo-show",20000,25000,0,"original"),
        ("asset-copy","event-1","demo-show",0,5000,20000,"excerpt"),
        ("asset-repeat","event-2","demo-repeat",10000,15000,0,"original")):
        write("asset",{"id":aid,"event_id":eid,"observation_id":oid,"rights_id":"demo-rights",
            "url":f"https://example.org/{aid}","role":role,"duration_ms":60000,"event_offset_ms":offset,
            "alignment_reviewed_by":"synthetic-fixture","alignment_evidence":"Known synthetic timeline offsets"})
        tid=f"transcript-{aid}";mid=f"mapping-{aid}";uid=f"utterance-{aid}";cid=f"occurrence-{aid}"
        write("transcript",{"id":tid,"asset_id":aid,"engine":"synthetic-fixture","segments":[
            {"start_ms":start,"end_ms":end,"speaker_label":"speaker_0","text":"Synthetic Lab processed 200 samples in 2025."}]})
        write("speaker_mapping",{"id":mid,"transcript_id":tid,"speaker_label":"speaker_0","person_id":PERSON_ID,
            "status":"confirmed","evidence":["Synthetic known speaker"],"reviewer":"synthetic-fixture"})
        write("utterance",{"id":uid,"transcript_id":tid,"mapping_id":mid,"appearance_id":f"appearance-{eid}",
            "segment_indices":[0],"exact_text":"Synthetic Lab processed 200 samples in 2025.","status":"accepted",
            "context_reviewed":True,"reviewer":"synthetic-fixture"})
        write("occurrence",{"id":cid,"utterance_id":uid,"proposition_id":"proposition-1","assertion":"asserted",
            "extraction_reviewed_by":"synthetic-fixture","extraction_rationale":"Literal synthetic assertion"})
    write("evidence",{"id":"evidence-1","observation_id":"demo-evidence","proposition_id":"proposition-1",
        "title":"Synthetic lab log","excerpt":"Synthetic Lab processed 100 completed samples in 2025.",
        "locator":"Synthetic document, entire line","relation":"conflicts","source_type":"primary","applicable_scope":scope})
    write("review",{"id":"review-1","proposition_id":"proposition-1","occurrence_ids":["occurrence-asset-original","occurrence-asset-copy","occurrence-asset-repeat"],
        "evidence_ids":["evidence-1"],"status":"reviewed","finding":"contradicted",
        "rationale":"Synthetic fixture: 200 differs from the synthetic primary log value of 100. No intent claim.",
        "reviewer":"synthetic-fixture","reviewed_at":"2026-09-27T00:00:00Z","scope_reviewed":True,
        "limitations":["Entirely fabricated test data, not a real-world investigation."]})
    write("coverage_run",{"id":"coverage-1","person_id":PERSON_ID,"source_id":"manual_import","query":"synthetic fixture",
         "period_start":"2025-05-01","period_end":"2025-05-02","retrieved":3,"processed":3,"state":"finished_query",
         "limitation":"Three fixture assets cover two synthetic events; no real-world completeness claim."})
    return ledger.person_ledger(PERSON_ID)
