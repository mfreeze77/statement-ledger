import copy,json
from datetime import datetime,timezone
import httpx,pytest
from statement_ledger.jev import JevClient,JevConfig,validate_response,strict_loads,ResponseContractError,run_decision
from statement_ledger.acceleration_demo import seed_acceleration
from statement_ledger.localization import semantic_request,plan_localization
from statement_ledger.acceleration import localize,match_claims
from statement_ledger.policy import PolicyError

QUESTIONS={"test":{"type":"noul","instructions":"Does the text match?"}}
def good(p=.9):return {"model":"jev-1.13.0","answers":{"test":{"type":"noul","noul":p}},"usage":{"input_tokens":12,"output_tokens":2}}

def test_official_endpoint_and_authorization():
    calls=[];captured=[]
    def handler(request):
        calls.append(request);return httpx.Response(200,json=good())
    with JevClient("test-secret",transport=httpx.MockTransport(handler)) as c:
        result=c.evaluate({"text":"data"},QUESTIONS,capture=lambda *x:captured.append(x) or "receipt")
    assert str(calls[0].url)=="https://api.typesafe.ai/v1/systemone"
    assert calls[0].headers["Authorization"]=="Bearer test-secret" and result["status"]=="available"
    assert b"test-secret" not in captured[0][2]

@pytest.mark.parametrize("value",[True,"0.9",-1,1.1,float('nan'),float('inf')])
def test_invalid_noul_values(value):
    with pytest.raises(ResponseContractError):validate_response(good(value),QUESTIONS,"jev-1.13.0")

@pytest.mark.parametrize("body",[b'{"a":1,"a":2}',b'{"a":NaN}',b'not json'])
def test_strict_json(body):
    with pytest.raises(ResponseContractError):strict_loads(body)

def test_raw_invalid_response_captured_before_rejection():
    captured=[]
    with JevClient("x",transport=httpx.MockTransport(lambda r:httpx.Response(200,content=b'{"bad":'))) as c:
        r=c.evaluate({},QUESTIONS,capture=lambda *args:captured.append(args) or "r1")
    assert captured[0][2]==b'{"bad":' and r["status"]=="unavailable" and r["answers"]=={}

def test_timeout_is_not_negative():
    def handler(r):raise httpx.ReadTimeout("failed",request=r)
    with JevClient("x",config=JevConfig(max_attempts=1),transport=httpx.MockTransport(handler)) as c:
        r=c.evaluate({},QUESTIONS,capture=lambda *a:"r")
    assert r["error_code"]=="transport_unavailable" and not r["answers"]

def test_missing_key_makes_no_request():
    def handler(r):raise AssertionError("Network must not be called")
    with JevClient("",transport=httpx.MockTransport(handler)) as c:
        r=c.evaluate({},QUESTIONS,capture=lambda *a:"r")
    assert r["error_code"]=="credentials_missing"

def test_request_size_budget():
    with JevClient("x",config=JevConfig(max_request_bytes=1024)) as c:
        r=c.evaluate("a"*4000,QUESTIONS,capture=lambda *a:"r")
    assert r["error_code"]=="request_byte_budget_exceeded"

def test_retry_after_bounded():
    calls=[];delays=[];receipts=[]
    def handler(r):
        calls.append(r)
        return httpx.Response(429,headers={"Retry-After":"999"},json={"error":"busy"}) if len(calls)==1 else httpx.Response(200,json=good())
    with JevClient("x",config=JevConfig(max_retry_seconds=.1),transport=httpx.MockTransport(handler),sleep=delays.append) as c:
        result=c.evaluate({},QUESTIONS,capture=lambda *a:receipts.append(a) or str(len(receipts)))
    assert len(calls)==2 and delays==[.1] and len(receipts)==2 and result["status"]=="available"

def test_schema_error_not_retried():
    calls=[]
    with JevClient("x",transport=httpx.MockTransport(lambda r:calls.append(r) or httpx.Response(200,json={}))) as c:
        result=c.evaluate({},QUESTIONS,capture=lambda *a:"r")
    assert len(calls)==1 and result["status"]=="unavailable"

def test_model_drift_is_fault():
    body=good();body["model"]="jev-9.0"
    with pytest.raises(ResponseContractError,match="model"):validate_response(body,QUESTIONS,"jev-1.13.0")

def test_question_ids_must_match():
    body=good();body["answers"]["other"]=body["answers"].pop("test")
    with pytest.raises(ResponseContractError):validate_response(body,QUESTIONS,"jev-1.13.0")

def test_independent_score_quantization_not_exact_math_fault():
    q={"x":{"type":"score","instructions":"Rate.","criteria":["low","middle","high"]}}
    raw={"model":"jev-1.13.0","answers":{"x":{"type":"score","score":.67,"legend":{"0":"low","1":"middle","2":"high"},"probabilities":{"0":.5,"1":.33,"2":.17},"confidence":.2}},"usage":{"input_tokens":10,"output_tokens":10}}
    # Expected 0.67; allow a separate 2dp quantized scalar of 0.68, with explicit warning.
    raw["answers"]["x"]["score"]=.68
    r=validate_response(raw,q,"jev-1.13.0")
    assert r["warnings"] and r["answers"]["x"]["score"]==.68
    raw["answers"]["x"]["score"]=1.8
    with pytest.raises(ResponseContractError):validate_response(raw,q,"jev-1.13.0")

def test_probability_total_not_silently_normalized():
    q={"x":{"type":"choice","instructions":"Choose.","criteria":{"a":"A","b":"B","c":"C"}}}
    raw={"model":"jev-1.13.0","answers":{"x":{"type":"choice","choice":"a","probabilities":{"a":.5,"b":.3,"c":.19},"confidence":.2}},"usage":{"input_tokens":1,"output_tokens":1}}
    r=validate_response(raw,q,"jev-1.13.0")
    assert r["answers"]["x"]["probabilities"]["c"]==.19 and r["warnings"]
    raw["answers"]["x"]["probabilities"]["a"]=.9
    with pytest.raises(ResponseContractError):validate_response(raw,q,"jev-1.13.0")

@pytest.fixture
def accelerated(ledger):seed_acceleration(ledger);return ledger

def dynamic_good(request):
    payload=json.loads(request.content)
    answers={key:{"type":q["type"],"noul":.8} for key,q in payload["questions"].items()}
    return httpx.Response(200,json={"model":payload["model"],"answers":answers,"usage":{"input_tokens":100,"output_tokens":20}})

def test_durable_capture_and_cache(accelerated):
    requests,issues=semantic_request(accelerated,"profile-demo","style-heldout-transcript")
    calls=[]
    with JevClient("x",transport=httpx.MockTransport(lambda r:calls.append(r) or dynamic_good(r))) as c:
        a=run_decision(accelerated,requests[0],c);b=run_decision(accelerated,requests[0],c)
    assert len(calls)==1 and b["cache_hit"] and a["record"]["id"]==b["record"]["id"]
    assert accelerated.store.verify_provider_receipts()["checked"]==1
    assert accelerated.store.verify_audit()["valid"]

def test_provider_rights_denied_before_network(seeded):
    row=seeded.store.get("transcript","transcript-asset-original")
    req={"state":"text","questions":QUESTIONS,"purpose":"speaker_localization","question_version":"v1","input_ids":[],"bindings":[{"kind":"transcript","id":row["id"],"revision":row["revision"]}]}
    with JevClient("x",transport=httpx.MockTransport(lambda r:pytest.fail("network forbidden"))) as c:
        with pytest.raises(PolicyError,match="send_to_provider"):run_decision(seeded,req,c)

def test_provider_fault_full_audio_fallback(accelerated):
    with JevClient("",transport=httpx.MockTransport(dynamic_good)) as c:
        result=localize(accelerated,"profile-demo","style-heldout-transcript",config={"mode":"assist"},use_jev=True,client=c)
    assert result["semantic_status"]=="unavailable"
    assert result["run"]["payload"]["selected_audio_ms"]==600000
    assert "semantic_evaluation_unavailable" in result["run"]["payload"]["fallback_reasons"]

def test_missing_question_window_does_not_authorize_skip(accelerated):
    batches,_=semantic_request(accelerated,"profile-demo","style-heldout-transcript")
    with JevClient("x",transport=httpx.MockTransport(dynamic_good)) as c:r=run_decision(accelerated,batches[0],c)
    plan=plan_localization(accelerated,"profile-demo","style-heldout-transcript",config={"mode":"assist"},decision_run_ids=[r["record"]["id"]])
    assert plan["payload"]["selected_audio_ms"]==600000 and "semantic_windows_incomplete" in plan["payload"]["fallback_reasons"]

def test_raw_receipt_tampering_detected(accelerated):
    batches,_=semantic_request(accelerated,"profile-demo","style-heldout-transcript")
    with JevClient("x",transport=httpx.MockTransport(dynamic_good)) as c:r=run_decision(accelerated,batches[0],c)
    accelerated.store.db.execute("UPDATE provider_receipts SET body=?",(b'changed',))
    assert not accelerated.store.verify_provider_receipts()["valid"]

def test_model_cache_input_revision_in_key(accelerated):
    batches,_=semantic_request(accelerated,"profile-demo","style-heldout-transcript")
    calls=[]
    with JevClient("x",transport=httpx.MockTransport(lambda r:calls.append(r) or dynamic_good(r))) as c:
        a=run_decision(accelerated,batches[0],c)
        changed=copy.deepcopy(batches[0]);changed["state"]["test_context"]="changed"
        b=run_decision(accelerated,changed,c)
    assert len(calls)==2 and not b["cache_hit"]

def test_no_live_model_enabled_by_default(accelerated,monkeypatch):
    monkeypatch.delenv("SL_ENABLE_JEV",raising=False)
    with pytest.raises(PolicyError,match="disabled"):localize(accelerated,"profile-demo","style-heldout-transcript",use_jev=True)

def choice_good(request):
    payload=json.loads(request.content)
    answers={key:{"type":"choice","choice":"same_scoped_assertion",
        "probabilities":{"same_scoped_assertion":.9,"related_but_different":.04,"unrelated":.02,"uncertain":.04},
        "confidence":.7} for key in payload["questions"]}
    return httpx.Response(200,json={"model":payload["model"],"answers":answers,"usage":{"input_tokens":200,"output_tokens":40}})

def test_claim_match_is_advisory_and_cached(accelerated):
    original=accelerated.store.get('proposition','proposition-1')['payload']
    candidate=copy.deepcopy(original);candidate['id']='matching-candidate'
    accelerated.put('proposition',candidate)
    before=accelerated.store.counts().get('review',0);calls=[]
    with JevClient('x',transport=httpx.MockTransport(lambda r:calls.append(r) or choice_good(r))) as client:
        first=match_claims(accelerated,'proposition-1',['matching-candidate'],client=client)
        second=match_claims(accelerated,'proposition-1',['matching-candidate'],client=client)
    assert len(calls)==1 and second['cache_hit']
    assert first['status']=='available' and first['items'][0]['scope_gate']['compatible_candidate']
    assert not first['automatic_review_reuse'] and accelerated.store.counts().get('review',0)==before

def test_semantic_claim_similarity_cannot_override_scope_difference(accelerated):
    candidate=copy.deepcopy(accelerated.store.get('proposition','proposition-1')['payload'])
    candidate['id']='different-year-candidate';candidate['scope']['period']='2099'
    accelerated.put('proposition',candidate)
    with JevClient('x',transport=httpx.MockTransport(choice_good)) as client:
        result=match_claims(accelerated,'proposition-1',['different-year-candidate'],client=client)
    assert result['items'][0]['semantic_answer']['choice']=='same_scoped_assertion'
    assert not result['items'][0]['scope_gate']['compatible_candidate']
    assert not result['automatic_review_reuse']

def test_full_semantic_localization_second_run_uses_cache(accelerated):
    calls=[]
    with JevClient('x',transport=httpx.MockTransport(lambda r:calls.append(r) or dynamic_good(r))) as client:
        first=localize(accelerated,'profile-demo','style-heldout-transcript',config={'mode':'assist'},use_jev=True,client=client)
        initial_calls=len(calls)
        second=localize(accelerated,'profile-demo','style-heldout-transcript',config={'mode':'assist'},use_jev=True,client=client)
    assert first['semantic_status']=='available' and initial_calls>1
    assert len(calls)==initial_calls and second['cache_hits']==initial_calls
    assert first['run']['id']==second['run']['id']
    assert first['run']['payload']['selected_audio_ms']==600000
    assert not first['run']['payload']['identities_confirmed']

def test_backup_preserves_non_utf8_receipt_bytes(accelerated):
    import base64
    raw=b'\xff\x00malformed-provider-payload'
    accelerated.store.capture_provider_response('a'*64,1,500,raw,False,{})
    exported=accelerated.store.export()['provider_receipts']
    assert base64.b64decode(exported[-1]['body_base64'])==raw
