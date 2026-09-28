from __future__ import annotations
from typing import Any
from .models import KINDS, RightsGrant, now
from .policy import PolicyError, require_right
from .store import Store, Missing
from .util import digest, canonical_url

class Ledger:
    def __init__(self, store: Store):
        self.store = store

    def put(self, kind: str, data: dict[str,Any], expected_revision: int = 0, actor: str = "local-operator") -> dict:
        if kind not in KINDS:
            raise ValueError(f"Unknown record kind: {kind}")
        if not actor.strip():
            raise ValueError("Actor is required")
        if expected_revision < 0:
            raise ValueError("Expected revision cannot be negative")
        model = KINDS[kind].model_validate(data)
        payload = model.model_dump(mode="json")
        with self.store.transaction():
            dependencies: dict[tuple[str,str],dict] = {}
            def ref(k: str, rid: str) -> dict:
                record = self.store.get(k,rid)
                if record["stale"] or not self.dependencies_current(k,rid):
                    raise PolicyError(f"Stale dependency: {k}:{rid}; revalidate it first")
                if self.store.would_cycle((kind,model.id),(k,rid)):
                    raise PolicyError("Dependency would create a cycle")
                dependencies[(k,rid)] = {"kind":k,"id":rid,"revision":record["revision"]}
                return record["payload"]
            self._validate(kind,payload,ref)
            return self.store.write(kind,payload,sorted(dependencies.values(),key=lambda x:(x["kind"],x["id"])),expected_revision,actor)

    def _validate(self, kind, p, ref):
        from .acceleration_models import EXTENSION_KINDS
        if kind in EXTENSION_KINDS:
            from .acceleration_service import validate_extension
            return validate_extension(self,kind,p,ref)
        if kind == "person":
            for url in p["identity_urls"]:
                canonical_url(url)
        elif kind == "rights":
            from .connectors.registry import source
            source(p["source_id"])
            if p["evidence_url"]:
                canonical_url(p["evidence_url"])
        elif kind == "observation":
            from .connectors.registry import source
            source(p["source_id"])
            grant = RightsGrant.model_validate(ref("rights",p["rights_id"]))
            require_right(grant,"store_text",p["source_id"])
            canonical_url(p["url"])
            for url in p["links"]:
                canonical_url(url)
            if digest(p["raw_payload"]) != p["raw_sha256"]:
                raise PolicyError("Raw payload checksum does not match")
        elif kind == "event":
            for oid in p["observation_ids"]:
                ref("observation",oid)
        elif kind == "appearance":
            ref("event",p["event_id"]); ref("person",p["person_id"])
            for oid in p["observation_ids"]:
                ref("observation",oid)
        elif kind == "asset":
            ref("event",p["event_id"])
            obs = ref("observation",p["observation_id"])
            grant = RightsGrant.model_validate(ref("rights",p["rights_id"]))
            require_right(grant,"discover",obs["source_id"])
            canonical_url(p["url"])
            if p["event_offset_ms"] is not None and type(p["event_offset_ms"]) is not int:
                raise PolicyError("Event offset must be integer milliseconds")
        elif kind == "transcript":
            asset = ref("asset",p["asset_id"])
            grant = RightsGrant.model_validate(ref("rights",asset["rights_id"]))
            require_right(grant,"store_text")
            if p["input_sha256"] and p["input_sha256"] != asset["content_sha256"]:
                raise PolicyError("Transcript input hash does not match the registered source asset")
            last_start = -1
            for s in p["segments"]:
                if s["end_ms"] > asset["duration_ms"]:
                    raise PolicyError("Transcript segment exceeds asset duration")
                if s["start_ms"] < last_start:
                    raise PolicyError("Segments must be sorted by start time; overlap remains allowed")
                last_start = s["start_ms"]
        elif kind == "speaker_mapping":
            transcript = ref("transcript",p["transcript_id"])
            ref("person",p["person_id"])
            if p["speaker_label"] not in {s["speaker_label"] for s in transcript["segments"]}:
                raise PolicyError("Speaker label is absent from this transcript")
            if p["status"] == "confirmed":
                if p["speaker_label"] in {"unassigned","unknown"}:
                    raise PolicyError("Unassigned audio must be diarized or manually segmented before naming a person")
                for row in self.store.all("speaker_mapping"):
                    other = row["payload"]
                    if other["id"] != p["id"] and not row["stale"] and other["status"] == "confirmed" and other["transcript_id"] == p["transcript_id"] and other["speaker_label"] == p["speaker_label"]:
                        raise PolicyError("This transcript label already has a confirmed mapping; revise that record")
        elif kind == "utterance":
            transcript = ref("transcript",p["transcript_id"])
            mapping = ref("speaker_mapping",p["mapping_id"])
            appearance = ref("appearance",p["appearance_id"])
            asset = ref("asset",transcript["asset_id"])
            if mapping["transcript_id"] != p["transcript_id"]:
                raise PolicyError("Speaker mapping belongs to another transcript")
            if appearance["person_id"] != mapping["person_id"] or appearance["event_id"] != asset["event_id"]:
                raise PolicyError("Appearance, person, and original event do not agree")
            indices = p["segment_indices"]
            if indices != list(range(indices[0],indices[-1]+1)):
                raise PolicyError("Utterance indices must be a nonduplicated contiguous range")
            if indices[-1] >= len(transcript["segments"]):
                raise PolicyError("Segment index out of bounds")
            segments = [transcript["segments"][i] for i in indices]
            if any(s["speaker_label"] != mapping["speaker_label"] for s in segments):
                raise PolicyError("Utterance contains words from another speaker")
            if p["exact_text"] != " ".join(s["text"] for s in segments):
                raise PolicyError("Exact text must match retained transcript segments verbatim")
            if p["status"] == "accepted":
                if not p["reviewer"] or not p["context_reviewed"] or mapping["status"] != "confirmed" or appearance["status"] != "confirmed":
                    raise PolicyError("Acceptance requires confirmed identity/appearance and context review")
                if any(s["overlap"] for s in segments) and not p["overlap_resolved"]:
                    raise PolicyError("Overlapping speech requires explicit resolution")
        elif kind == "proposition":
            for oid in p["seed_observation_ids"]:ref("observation",oid)
        elif kind == "occurrence":
            utterance = ref("utterance",p["utterance_id"])
            ref("proposition",p["proposition_id"])
            if p["extraction_reviewed_by"] and (utterance["status"] != "accepted" or not p["extraction_rationale"]):
                raise PolicyError("Reviewed extraction requires accepted utterance and rationale")
        elif kind == "evidence":
            ref("proposition",p["proposition_id"])
            obs = ref("observation",p["observation_id"])
            text = obs.get("text")
            if not text or p["excerpt"] not in text:
                raise PolicyError("Evidence excerpt must occur verbatim in the retained observation text")
            if p["source_type"] == "primary" and obs["kind"] in {"external_review","media_review"}:
                raise PolicyError("External reviews cannot be relabeled as primary evidence")
        elif kind == "review":
            prop = ref("proposition",p["proposition_id"])
            occurrences = [ref("occurrence",oid) for oid in p["occurrence_ids"]]
            evidence = [ref("evidence",eid) for eid in p["evidence_ids"]]
            if any(o["proposition_id"] != p["proposition_id"] for o in occurrences):
                raise PolicyError("Review occurrences refer to another proposition")
            if any(e["proposition_id"] != p["proposition_id"] for e in evidence):
                raise PolicyError("Review evidence belongs to another proposition")
            if p["status"] == "reviewed":
                if not p["reviewer"] or not p["reviewed_at"] or not p["scope_reviewed"]:
                    raise PolicyError("Completed review requires reviewer, date, and explicit scope review")
                if any(not o["extraction_reviewed_by"] or o["assertion"] != "asserted" for o in occurrences):
                    raise PolicyError("Completed factual review requires reviewed asserted occurrences")
                if p["finding"] in {"supported","contradicted","mixed"}:
                    if prop["kind"] != "empirical" or not evidence:
                        raise PolicyError("A factual finding requires an empirical proposition and evidence")
                    for e in evidence:
                        if e["relation"] in {"supports","conflicts"}:
                            for field in ("entity","metric","geography","period","unit","definition","baseline","comparator","polarity","conditions","population","accounting_basis","document_version"):
                                if e["applicable_scope"].get(field) != prop["scope"].get(field):
                                    raise PolicyError("Evidence scope mismatch; do not reuse a different proposition")
                            if any(not prop["scope"][key] for key in ("entity","metric","geography","period","unit","definition")):
                                raise PolicyError("Complete factual scope or mark explicitly not_applicable before review")
                    if not any(e["source_type"] == "primary" and e["relation"] in {"supports","conflicts"} for e in evidence):
                        raise PolicyError("A completed factual finding needs underlying primary evidence")
                if p["finding"] == "contradicted" and not any(e["relation"] == "conflicts" and e["source_type"] == "primary" for e in evidence):
                    raise PolicyError("Contradicted finding requires conflicting evidence")
                if p["finding"] == "supported" and not any(e["relation"] == "supports" and e["source_type"] == "primary" for e in evidence):
                    raise PolicyError("Supported finding requires supporting evidence")
                if p["finding"] == "mixed" and not ({"supports","conflicts"} <= {e["relation"] for e in evidence}):
                    raise PolicyError("Mixed finding requires supporting and conflicting evidence")
        elif kind == "correction":
            if p["target_kind"] not in KINDS:
                raise PolicyError("Unknown correction target kind")
            ref(p["target_kind"],p["target_id"]); ref("observation",p["observation_id"])
            if p["status"] in {"verified","resolved"} and not p["reviewer"]:
                raise PolicyError("Verified/resolved correction needs a reviewer")
            if p["status"] == "resolved" and (not p["resolution"] or not p["resolved_at"]):
                raise PolicyError("Resolved correction needs a dated resolution")
        elif kind == "coverage_run":
            ref("person",p["person_id"])
            from .connectors.registry import source
            source(p["source_id"])
            if p["processed"] > p["retrieved"]:
                raise PolicyError("Processed count exceeds retrieved count")
            if p["period_end"] < p["period_start"]:
                raise PolicyError("Coverage end precedes start")

    def dependencies_current(self, kind: str, record_id: str) -> bool:
        todo,seen=[(kind,record_id)],set()
        while todo:
            key=todo.pop()
            if key in seen: continue
            seen.add(key)
            row=self.store.get(*key)
            if row["stale"]: return False
            if key[0]=="rights":
                grant=RightsGrant.model_validate(row["payload"])
                if grant.expires_at and grant.expires_at<=now(): return False
            for d in row["dependencies"]:
                parent=self.store.get(d["kind"],d["id"])
                if parent["revision"] != d["revision"]: return False
                todo.append((d["kind"],d["id"]))
        return True

    def person_ledger(self, person_id: str) -> dict:
        person = self.store.get("person",person_id)
        items, exclusions = [], []
        relevant_keys = {("person",person_id)}
        def collect(kind,rid):
            todo=[(kind,rid)]
            while todo:
                key=todo.pop()
                if key in relevant_keys: continue
                relevant_keys.add(key)
                record=self.store.get(*key)
                todo.extend((d["kind"],d["id"]) for d in record["dependencies"])

        for row in self.store.all("occurrence"):
            p = row["payload"]
            try:
                u = self.store.get("utterance",p["utterance_id"])
                m = self.store.get("speaker_mapping",u["payload"]["mapping_id"])
                if m["payload"]["person_id"] != person_id:
                    continue
                collect("occurrence",p["id"])
                t = self.store.get("transcript",u["payload"]["transcript_id"])
                a = self.store.get("asset",t["payload"]["asset_id"])
                appearance = self.store.get("appearance",u["payload"]["appearance_id"])
                prop = self.store.get("proposition",p["proposition_id"])
                reason = None
                if not self.dependencies_current("occurrence",p["id"]):
                    reason = "stale_dependency"
                elif u["payload"]["status"] != "accepted" or not p["extraction_reviewed_by"]:
                    reason = "review_incomplete"
                elif p["assertion"] != "asserted":
                    reason = "not_an_assertion"
                elif a["payload"]["event_offset_ms"] is None:
                    reason = "unresolved_event_alignment"
                else:
                    rights = self.store.get("rights",a["payload"]["rights_id"])
                    try:
                        require_right(RightsGrant.model_validate(rights["payload"]),"store_text")
                    except PolicyError:
                        reason = "rights_not_current"
                if reason:
                    exclusions.append({"occurrence_id":p["id"],"reason":reason}); continue
                indices = u["payload"]["segment_indices"]
                segments = [t["payload"]["segments"][i] for i in indices]
                start = segments[0]["start_ms"] + a["payload"]["event_offset_ms"]
                end = segments[-1]["end_ms"] + a["payload"]["event_offset_ms"]
                if start < 0:
                    exclusions.append({"occurrence_id":p["id"],"reason":"invalid_event_alignment"}); continue
                key = digest([a["payload"]["event_id"],person_id,p["proposition_id"],start,end])
                reviews = [r for r in self.store.all("review") if p["id"] in r["payload"]["occurrence_ids"] and r["payload"]["status"]=="reviewed" and self.dependencies_current("review",r["id"])]
                for reviewed in reviews: collect("review",reviewed["id"])
                items.append({"occurrence_id":p["id"],"canonical_key":key,"event_id":a["payload"]["event_id"],
                              "asset_id":a["id"],"asset_role":a["payload"]["role"],"proposition_id":p["proposition_id"],
                              "exact_text":u["payload"]["exact_text"],"event_start_ms":start,"event_end_ms":end,
                              "source_start_ms":segments[0]["start_ms"],"source_end_ms":segments[-1]["end_ms"],
                              "source_url":a["payload"]["url"],"reviews":reviews})
            except Missing:
                exclusions.append({"occurrence_id":p["id"],"reason":"missing_dependency"})
        appearances = [a for a in self.store.all("appearance") if a["payload"]["person_id"] == person_id]
        coverage = [c for c in self.store.all("coverage_run") if c["payload"]["person_id"] == person_id]
        return {"person":person,"items":items,"exclusions":exclusions,"appearances":appearances,"coverage":coverage,
                "counts":{"eligible_recorded_assertion_rows":len(items),"distinct_aligned_assertion_occurrences":len({i["canonical_key"] for i in items}),
                          "distinct_propositions":len({i["proposition_id"] for i in items}),"excluded_rows":len(exclusions)},
                "coverage_statement":"Identified records only; not all appearances or all statements.",
                "deduplication_limit":"Exact human-reviewed event coordinates only; fuzzy offset reconciliation is not implemented.",
                "corrections":[c for c in self.store.all("correction") if (c["payload"]["target_kind"],c["payload"]["target_id"]) in relevant_keys],
                "person_rating":None}
