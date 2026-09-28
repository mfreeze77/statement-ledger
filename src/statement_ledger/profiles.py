"""Learn event-normalized phrase features from accepted, source-bound turns only."""
from __future__ import annotations
import math, re, unicodedata
from collections import defaultdict
from .models import RightsGrant
from .acceleration_models import SpeakerProfile, ProfileConfig
from .policy import PolicyError, require_right

TOKENIZER_VERSION="unicode-words-v1"
def tokens(text):
    # Not ASCII-only: keep Unicode letters and normalize apostrophe variants.
    return re.findall(r"[^\W_]+(?:['’][^\W_]+)*",unicodedata.normalize("NFKC",text).casefold().replace("’","'"),re.UNICODE)

def binding(row):
    return {"kind":row["kind"],"id":row["id"],"revision":row["revision"]}

def current(ledger,kind,rid):
    row=ledger.store.get(kind,rid)
    if not ledger.dependencies_current(kind,rid): raise PolicyError(f"Stale or expired source: {kind}:{rid}")
    return row

def example(ledger,uid):
    u=current(ledger,"utterance",uid);p=u["payload"]
    if p["status"]!="accepted": raise PolicyError("Only accepted speaking turns can train a profile")
    m=current(ledger,"speaker_mapping",p["mapping_id"])
    t=current(ledger,"transcript",p["transcript_id"])
    a=current(ledger,"asset",t["payload"]["asset_id"])
    grant=current(ledger,"rights",a["payload"]["rights_id"])
    require_right(RightsGrant.model_validate(grant["payload"]),"learn_profile")
    if m["payload"]["status"]!="confirmed":raise PolicyError("Profile identity must be confirmed")
    return {"id":uid,"person_id":m["payload"]["person_id"],"event_id":a["payload"]["event_id"],
        "text":p["exact_text"],"binding":binding(u),"language":t["payload"]["language"]}

def features_for(text,config):
    words=tokens(text);result=set()
    for n in range(config.min_ngram,config.max_ngram+1):
        if len(words)<n:continue
        result.add(("opening"," ".join(words[:n])))
        result.add(("closing"," ".join(words[-n:])))
        result.update(("phrase"," ".join(words[i:i+n])) for i in range(len(words)-n+1))
    return result

def derive_profile(ledger, person_id, example_ids, background_ids, config=None):
    config=ProfileConfig.model_validate(config or {})
    person=current(ledger,"person",person_id)
    if set(example_ids)&set(background_ids):raise PolicyError("Target and background samples overlap")
    target=[example(ledger,x) for x in sorted(set(example_ids))]
    background=[example(ledger,x) for x in sorted(set(background_ids))]
    if any(x["person_id"]!=person_id for x in target):raise PolicyError("Target sample belongs to another person")
    if any(x["person_id"]==person_id for x in background):raise PolicyError("Background cannot contain the target")
    counts=[defaultdict(set),defaultdict(set)];events=[set(),set()];seen=set();retained=[];duplicates=[]
    for group,rows in enumerate((target,background)):
        for row in rows:
            # One evidence point per event/phrase, irrespective of reposts or repeated turns.
            key=(row["person_id"],row["event_id"],tuple(tokens(row["text"])))
            if key in seen:duplicates.append(row["id"]);continue
            seen.add(key);retained.append(row["id"]);events[group].add(row["event_id"])
            for feature in features_for(row["text"],config):counts[group][feature].add(row["event_id"])
    n,m=len(events[0]),len(events[1]);out=[]
    for key,event_ids in counts[0].items():
        a,b=len(event_ids),len(counts[1][key])
        if a<config.min_feature_events:continue
        weight=math.log((a+0.5)/(n-a+0.5))-math.log((b+0.5)/(m-b+0.5))
        if weight>0:out.append({"category":key[0],"phrase":key[1],"target_events":a,"background_events":b,"weight":round(weight,8)})
    out.sort(key=lambda x:(-x["weight"],-x["target_events"],x["category"],x["phrase"]))
    ready=n>=config.min_events and m>=config.min_background_events and bool(out)
    return {"person_id":person_id,"example_ids":sorted(set(example_ids)),"background_ids":sorted(set(background_ids)),
        "config":config.model_dump(),"algorithm":"event-log-odds-v1","features":out[:config.max_features],
        "target_event_ids":sorted(events[0]),"background_event_ids":sorted(events[1]),
        "retained_example_ids":sorted(retained),"duplicate_example_ids":sorted(duplicates),
        "bindings":[binding(person)]+[r["binding"] for r in target+background],
        "readiness":"research_ready" if ready else "cold_start","calibration":"uncalibrated",
        "limitations":["Language patterns are discovery signals, not identity proof.",
        "Features count events, not uploads or raw repetitions.",
        "Tokenizer/prefix boundaries are transcript-dependent; no automatic morphological or rhetorical classifier.",
        "Background selection, topics, dates, programs and caption quality require held-out evaluation."]}

def build_profile(ledger,person_id,example_ids,background_ids,*,profile_id=None,config=None,expected_revision=0,actor="local-operator"):
    payload=derive_profile(ledger,person_id,example_ids,background_ids,config)
    payload["id"]=profile_id or f"profile-{person_id}"
    return ledger.put("speaker_profile",payload,expected_revision,actor)

def lexical_features(profile,text):
    words=tokens(text);joined=" "+" ".join(words)+" ";matches=[];best={}
    for f in profile["features"]:
        # Caption-window boundaries are not known turn boundaries. All pattern types
        # are presence clues here; the category still describes the training turn.
        if " "+f["phrase"]+" " in joined:
            matches.append(f'{f["category"]}:{f["phrase"]}')
            best[f["phrase"]]=max(best.get(f["phrase"],0),f["weight"])
    # Avoid inflating a nested phrase by summing every ngram variant.
    score=max(best.values(),default=0.0)
    return score,sorted(matches)


def refresh_profile(ledger,profile_id,*,background_person_ids=None,holdout_event_ids=None,actor="local-operator"):
    """Explicit incremental rebuild from current accepted turns, never guesses.

Holdout events remain excluded from BOTH classes. Caller chooses comparison people;
we do not infer affiliations or choose ideological comparison groups.
"""
    old=ledger.store.get("speaker_profile",profile_id) # Read stale configuration; rebuild from current sources.
    p=old["payload"];background_person_ids=set(background_person_ids or [])
    if p["person_id"] in background_person_ids:raise PolicyError("Target cannot be a background person")
    holdout=set(holdout_event_ids or []);target=[];background=[];excluded=[]
    # Reference workspace scan; production refresh workers should query accepted-turn projections.
    for row in ledger.store.all("utterance"):
        if row["payload"]["status"]!="accepted":continue
        try:item=example(ledger,row["id"])
        except PolicyError:
            excluded.append({"utterance_id":row["id"],"reason":"stale_or_permission_blocked"});continue
        if item["event_id"] in holdout:
            excluded.append({"utterance_id":row["id"],"reason":"held_out_event"});continue
        if item["person_id"]==p["person_id"]:target.append(row["id"])
        elif item["person_id"] in background_person_ids:background.append(row["id"])
    if not background_person_ids:
        # Preserve an explicitly curated background set rather than choose one silently.
        background=[]
        for rid in p["background_ids"]:
            try:
                if example(ledger,rid)["event_id"] not in holdout:background.append(rid)
            except PolicyError:excluded.append({"utterance_id":rid,"reason":"stale_or_permission_blocked_background"})
    result=build_profile(ledger,p["person_id"],target,background,profile_id=profile_id,config=p["config"],expected_revision=old["revision"],actor=actor)
    return {"profile":result,"excluded":excluded,"new_examples":len(set(target)-set(p["example_ids"])),"automatically_confirmed_turns":0}
