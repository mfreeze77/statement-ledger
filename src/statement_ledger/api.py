"""Authenticated single-workspace operator API, not a public SaaS deployment."""
from __future__ import annotations
import os,secrets
from pathlib import Path
from typing import Annotated
from importlib.resources import files
from fastapi import FastAPI,Depends,HTTPException,Header,Query,Request
from fastapi.responses import HTMLResponse,Response,JSONResponse
from pydantic import BaseModel,ConfigDict,Field,ValidationError
from .models import KINDS,Scope
from .store import Store,Conflict,Missing
from .service import Ledger
from .connectors.registry import sources
from .discovery import plan_person
from .media import clip_plan
from .policy import scope_match

class Input(BaseModel):model_config=ConfigDict(extra="forbid")
class PutInput(Input):
    record: dict
    expected_revision: int=Field(default=0,ge=0,strict=True)
class PlanInput(Input):
    name: str=Field(min_length=1,max_length=250)
    aliases: list[str]=Field(default_factory=list,max_length=50)
class ScopeInput(Input):left: Scope;right: Scope
class ClipInput(Input):
    start_ms: int=Field(ge=0,strict=True)
    end_ms: int=Field(gt=0,strict=True)
    duration_ms: int=Field(gt=0,strict=True)
    padding_ms: int=Field(default=15000,ge=0,strict=True)

from .acceleration_models import ProfileConfig,LocalizationConfig
class ProfileBuildInput(Input):
    person_id: str
    example_ids: list[str]=Field(default_factory=list,max_length=10000)
    background_ids: list[str]=Field(default_factory=list,max_length=10000)
    profile_id: str|None=None
    config: ProfileConfig=Field(default_factory=ProfileConfig)
    expected_revision: int=Field(default=0,ge=0,strict=True)
class ProfileRefreshInput(Input):
    background_person_ids: list[str]=Field(default_factory=list,max_length=100)
    holdout_event_ids: list[str]=Field(default_factory=list,max_length=10000)
class LocalizationInput(Input):
    profile_id: str
    transcript_id: str
    config: LocalizationConfig=Field(default_factory=LocalizationConfig)
    use_jev: bool=False
    max_calls: int=Field(default=16,ge=1,le=100)
class ClaimSearchInput(Input):
    text: str=Field(min_length=1,max_length=10000)
    scope: Scope|None=None
    limit: int=Field(default=20,ge=1,le=100)
class ClaimMatchInput(Input):
    proposition_id: str
    candidate_ids: list[str]=Field(min_length=1,max_length=16)
class WorkInput(Input):
    run_ids: list[str]=Field(min_length=1,max_length=100)

def create_app(db_path: str|None=None,token: str|None=None) -> FastAPI:
    path=db_path or os.environ.get("SL_DB_PATH","data/ledger.sqlite3")
    secret=token or os.environ.get("SL_API_TOKEN","")
    if len(secret)<32:raise RuntimeError("SL_API_TOKEN must be configured with at least 32 characters")
    app=FastAPI(title="Statement Ledger",version="0.2.0",docs_url=None,redoc_url=None,openapi_url=None)
    def auth(authorization: Annotated[str|None,Header()]=None):
        if not authorization or not authorization.startswith("Bearer ") or not secrets.compare_digest(authorization[7:],secret):
            raise HTTPException(401,"Bearer authentication required",headers={"WWW-Authenticate":"Bearer"})
        return "local-owner" # Trusted authenticated identity, never a caller-supplied actor name.
    def ledger_dep():
        store=Store(path)
        try:yield Ledger(store)
        finally:store.close()
    Actor=Depends(auth);DB=Depends(ledger_dep)
    @app.middleware("http")
    async def headers_and_size(request: Request,call_next):
        if request.method in {"POST","PUT","PATCH"}:
            # Actual bounded read, not only trusting Content-Length.
            chunks=[];size=0
            async for chunk in request.stream():
                size+=len(chunk)
                if size>4*1024*1024:return JSONResponse({"detail":"Request exceeds 4 MiB limit"},status_code=413)
                chunks.append(chunk)
            request._body=b"".join(chunks)
        response=await call_next(request)
        response.headers["X-Content-Type-Options"]="nosniff"
        response.headers["Referrer-Policy"]="no-referrer"
        response.headers["Cache-Control"]="no-store"
        response.headers["Content-Security-Policy"]="default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self'; frame-ancestors 'none'; base-uri 'none'"
        return response
    @app.exception_handler(Conflict)
    async def conflict_handler(req,exc):return JSONResponse({"detail":str(exc)},status_code=409)
    @app.exception_handler(Missing)
    async def missing_handler(req,exc):return JSONResponse({"detail":"Record not found"},status_code=404)
    @app.exception_handler(ValueError)
    async def value_handler(req,exc):
        # Pydantic errors may include large submitted content; return a bounded explanation.
        detail="Record validation failed" if isinstance(exc,ValidationError) else str(exc)[:1000]
        return JSONResponse({"detail":detail},status_code=422)
    @app.get("/healthz")
    def health():return {"service":"statement-ledger","version":"0.2.0","mode":"single-workspace-reference"}
    @app.get("/",response_class=HTMLResponse)
    def index():return files("statement_ledger").joinpath("static/index.html").read_text(encoding="utf-8")
    @app.get("/static/{name}")
    def static(name: str):
        if name not in {"app.js","style.css"}:raise HTTPException(404)
        return Response(files("statement_ledger").joinpath("static",name).read_text(encoding="utf-8"),media_type="text/javascript" if name.endswith(".js") else "text/css")
    @app.get("/api/openapi.json")
    def openapi(actor=Actor):return app.openapi()
    @app.get("/api/sources")
    def registry(actor=Actor):return {"sources":sources()}
    @app.get("/api/counts")
    def counts(actor=Actor,ledger=DB):return ledger.store.counts()
    @app.get("/api/schema/{kind}")
    def schema(kind: str,actor=Actor):
        if kind not in KINDS:raise HTTPException(404,"Unknown record kind")
        return KINDS[kind].model_json_schema()
    @app.get("/api/records/{kind}")
    def records(kind: str,limit: int=Query(100,ge=1,le=1000),offset: int=Query(0,ge=0),actor=Actor,ledger=DB):
        if kind not in KINDS:raise HTTPException(404,"Unknown record kind")
        return {"items":ledger.store.list(kind,limit,offset),"limit":limit,"offset":offset}
    @app.get("/api/records/{kind}/{record_id}")
    def record(kind: str,record_id: str,revision: int|None=Query(None,ge=1),actor=Actor,ledger=DB):
        return ledger.store.get(kind,record_id,revision)
    @app.get("/api/history/{kind}/{record_id}")
    def history(kind: str,record_id: str,actor=Actor,ledger=DB):return {"items":ledger.store.history(kind,record_id)}
    @app.post("/api/records/{kind}")
    def write(kind: str,body: PutInput,actor=Actor,ledger=DB):
        return ledger.put(kind,body.record,body.expected_revision,actor)
    @app.get("/api/people/{person_id}/ledger")
    def person(person_id: str,actor=Actor,ledger=DB):return ledger.person_ledger(person_id)
    @app.post("/api/discovery/plan")
    def plan(body: PlanInput,actor=Actor):return plan_person(body.name,body.aliases)
    @app.post("/api/scope/compare")
    def scope(body: ScopeInput,actor=Actor):return scope_match(body.left,body.right)
    @app.post("/api/clips/plan")
    def clips(body: ClipInput,actor=Actor):return clip_plan(**body.model_dump())
    @app.get("/api/integrity")
    def integrity(actor=Actor,ledger=DB):return {"audit":ledger.store.verify_audit(),"records":ledger.store.verify_records(),"provider_receipts":ledger.store.verify_provider_receipts()}
    @app.post("/api/profiles/build")
    def profile_build(body: ProfileBuildInput,actor=Actor,ledger=DB):
        from .profiles import build_profile
        return build_profile(ledger,**body.model_dump(),actor=actor)
    @app.post("/api/profiles/{profile_id}/refresh")
    def profile_refresh(profile_id: str,body: ProfileRefreshInput,actor=Actor,ledger=DB):
        from .profiles import refresh_profile
        return refresh_profile(ledger,profile_id,**body.model_dump(),actor=actor)
    @app.post("/api/localization/plan")
    def localization(body: LocalizationInput,actor=Actor,ledger=DB):
        from .acceleration import localize
        return localize(ledger,**body.model_dump(),actor=actor)
    @app.post("/api/localization/combine")
    def combine(body: WorkInput,actor=Actor,ledger=DB):
        from .localization import combined_work
        return combined_work(ledger,body.run_ids)
    @app.post("/api/claims/search")
    def claim_search(body: ClaimSearchInput,actor=Actor,ledger=DB):
        from .claim_library import search_claims
        return search_claims(ledger,**body.model_dump())
    @app.get("/api/claims/cards/{card_id}")
    def claim_card(card_id: str,actor=Actor,ledger=DB):
        from .claim_library import card_status
        return card_status(ledger,ledger.store.get("claim_card",card_id))
    @app.post("/api/claims/match")
    def claim_match(body: ClaimMatchInput,actor=Actor,ledger=DB):
        from .acceleration import match_claims
        return match_claims(ledger,**body.model_dump(),actor=actor)
    @app.get("/api/acceleration/status")
    def acceleration_status(actor=Actor,ledger=DB):
        return {"version":"0.2.0","jev_enabled":os.getenv("SL_ENABLE_JEV","0")=="1",
            "model":os.getenv("SL_JEV_MODEL","jev-1.13.0"),"speaker_identity_automatic":False,
            "verdict_reuse_automatic":False,"provider_receipts":ledger.store.verify_provider_receipts()}
    return app
