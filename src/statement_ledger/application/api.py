"""Authenticated single-workspace operator API, not a public SaaS deployment."""

from __future__ import annotations

import secrets
from importlib.resources import files
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from statement_ledger.application.ledger import Ledger
from statement_ledger.contracts.acceleration import LocalizationConfig, ProfileConfig
from statement_ledger.contracts.models import KINDS, Scope
from statement_ledger.contracts.runtime import JobRequest
from statement_ledger.contracts.source_catalog import sources
from statement_ledger.core.errors import Conflict, Missing
from statement_ledger.core.policy import scope_match
from statement_ledger.infrastructure.operations import OperationBlocked
from statement_ledger.infrastructure.sqlite_store import Store
from statement_ledger.pillars.discovery.planner import plan_person
from statement_ledger.pillars.media.clipping import clip_plan


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid")


class PutInput(Input):
    record: dict
    expected_revision: int = Field(default=0, ge=0, strict=True)


class PlanInput(Input):
    name: str = Field(min_length=1, max_length=250)
    aliases: list[str] = Field(default_factory=list, max_length=50)


class ScopeInput(Input):
    left: Scope
    right: Scope


class ClipInput(Input):
    start_ms: int = Field(ge=0, strict=True)
    end_ms: int = Field(gt=0, strict=True)
    duration_ms: int = Field(gt=0, strict=True)
    padding_ms: int = Field(default=15000, ge=0, strict=True)


class ProfileBuildInput(Input):
    person_id: str
    example_ids: list[str] = Field(default_factory=list, max_length=10000)
    background_ids: list[str] = Field(default_factory=list, max_length=10000)
    profile_id: str | None = None
    config: ProfileConfig = Field(default_factory=ProfileConfig)
    expected_revision: int = Field(default=0, ge=0, strict=True)


class ProfileRefreshInput(Input):
    background_person_ids: list[str] = Field(default_factory=list, max_length=100)
    holdout_event_ids: list[str] = Field(default_factory=list, max_length=10000)


class LocalizationInput(Input):
    profile_id: str
    transcript_id: str
    config: LocalizationConfig = Field(default_factory=LocalizationConfig)
    use_jev: bool = False
    max_calls: int = Field(default=16, ge=1, le=100)


class ClaimSearchInput(Input):
    text: str = Field(min_length=1, max_length=10000)
    scope: Scope | None = None
    limit: int = Field(default=20, ge=1, le=100)


class ClaimMatchInput(Input):
    proposition_id: str
    candidate_ids: list[str] = Field(min_length=1, max_length=16)


class WorkInput(Input):
    run_ids: list[str] = Field(min_length=1, max_length=100)


def create_app(db_path: str | None = None, token: str | None = None, settings=None) -> FastAPI:
    from statement_ledger.infrastructure.secrets import LocalSecrets
    from statement_ledger.infrastructure.settings import load_settings

    settings = settings or load_settings(overrides={"db_path": db_path} if db_path else {})
    path = str(settings.database)
    secret = token or LocalSecrets().value("API_TOKEN", required=False)
    if len(secret) < 32:
        raise RuntimeError("SL_API_TOKEN must be configured with at least 32 characters")
    startup = Store(path, journal_mode=settings.journal_mode)
    startup.close()
    app = FastAPI(
        title="Statement Ledger", version="0.3.0", docs_url=None, redoc_url=None, openapi_url=None
    )

    def auth(authorization: Annotated[str | None, Header()] = None):
        if (
            not authorization
            or not authorization.startswith("Bearer ")
            or not secrets.compare_digest(authorization[7:], secret)
        ):
            raise HTTPException(
                401, "Bearer authentication required", headers={"WWW-Authenticate": "Bearer"}
            )
        return "local-owner"  # Trusted authenticated identity, never a caller-supplied actor name.

    def ledger_dep():
        store = Store(path, journal_mode=settings.journal_mode)
        try:
            ledger = Ledger(store)
            ledger.settings = settings
            yield ledger
        finally:
            store.close()

    Actor = Depends(auth)
    DB = Depends(ledger_dep)

    @app.middleware("http")
    async def headers_and_size(request: Request, call_next):
        if request.method in {"POST", "PUT", "PATCH"}:
            # Actual bounded read, not only trusting Content-Length.
            chunks = []
            size = 0
            async for chunk in request.stream():
                size += len(chunk)
                if size > 4 * 1024 * 1024:
                    return JSONResponse({"detail": "Request exceeds 4 MiB limit"}, status_code=413)
                chunks.append(chunk)
            request._body = b"".join(chunks)
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "no-store"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self'; frame-ancestors 'none'; base-uri 'none'"
        )
        return response

    @app.exception_handler(Conflict)
    async def conflict_handler(req, exc):
        return JSONResponse({"detail": str(exc)}, status_code=409)

    @app.exception_handler(OperationBlocked)
    async def blocked_handler(req, exc):
        return JSONResponse(
            {"detail": "Provider operation requires budget or reconciliation; no automatic retry"},
            status_code=409,
        )

    @app.exception_handler(Missing)
    async def missing_handler(req, exc):
        return JSONResponse({"detail": "Record not found"}, status_code=404)

    @app.exception_handler(ValueError)
    async def value_handler(req, exc):
        # Pydantic errors may include large submitted content; return a bounded explanation.
        detail = "Record validation failed" if isinstance(exc, ValidationError) else str(exc)[:1000]
        return JSONResponse({"detail": detail}, status_code=422)

    @app.get("/healthz")
    def health():
        return {
            "service": "statement-ledger",
            "version": "0.3.0",
            "mode": "single-workspace-reference",
        }

    @app.get("/", response_class=HTMLResponse)
    def index():
        return files("statement_ledger").joinpath("static/index.html").read_text(encoding="utf-8")

    @app.get("/static/{name}")
    def static(name: str):
        if name not in {"app.js", "style.css"}:
            raise HTTPException(404)
        return Response(
            files("statement_ledger").joinpath("static", name).read_text(encoding="utf-8"),
            media_type="text/javascript" if name.endswith(".js") else "text/css",
        )

    @app.get("/api/openapi.json")
    def openapi(actor=Actor):
        return app.openapi()

    @app.get("/api/sources")
    def registry(actor=Actor):
        return {"sources": sources()}

    @app.get("/api/counts")
    def counts(actor=Actor, ledger=DB):
        return ledger.store.counts()

    @app.get("/api/schema/{kind}")
    def schema(kind: str, actor=Actor):
        if kind not in KINDS:
            raise HTTPException(404, "Unknown record kind")
        return KINDS[kind].model_json_schema()

    @app.get("/api/records/{kind}")
    def records(
        kind: str,
        limit: int = Query(100, ge=1, le=1000),
        offset: int = Query(0, ge=0),
        actor=Actor,
        ledger=DB,
    ):
        if kind not in KINDS:
            raise HTTPException(404, "Unknown record kind")
        return {"items": ledger.store.list(kind, limit, offset), "limit": limit, "offset": offset}

    @app.get("/api/records/{kind}/{record_id}")
    def record(
        kind: str, record_id: str, revision: int | None = Query(None, ge=1), actor=Actor, ledger=DB
    ):
        return ledger.store.get(kind, record_id, revision)

    @app.get("/api/history/{kind}/{record_id}")
    def history(kind: str, record_id: str, actor=Actor, ledger=DB):
        return {"items": ledger.store.history(kind, record_id)}

    @app.post("/api/records/{kind}")
    def write(kind: str, body: PutInput, actor=Actor, ledger=DB):
        return ledger.put(kind, body.record, body.expected_revision, actor)

    @app.get("/api/people/{person_id}/ledger")
    def person(person_id: str, actor=Actor, ledger=DB):
        return ledger.person_ledger(person_id)

    @app.post("/api/discovery/plan")
    def plan(body: PlanInput, actor=Actor):
        return plan_person(body.name, body.aliases)

    @app.post("/api/scope/compare")
    def scope(body: ScopeInput, actor=Actor):
        return scope_match(body.left, body.right)

    @app.post("/api/clips/plan")
    def clips(body: ClipInput, actor=Actor):
        return clip_plan(**body.model_dump())

    @app.get("/api/integrity")
    def integrity(actor=Actor, ledger=DB):
        return {
            "audit": ledger.store.verify_audit(),
            "records": ledger.store.verify_records(),
            "provider_receipts": ledger.store.verify_provider_receipts(),
        }

    @app.post("/api/profiles/build")
    def profile_build(body: ProfileBuildInput, actor=Actor, ledger=DB):
        from statement_ledger.pillars.speech.profiles import build_profile

        return build_profile(ledger, **body.model_dump(), actor=actor)

    @app.post("/api/profiles/{profile_id}/refresh")
    def profile_refresh(profile_id: str, body: ProfileRefreshInput, actor=Actor, ledger=DB):
        from statement_ledger.pillars.speech.profiles import refresh_profile

        return refresh_profile(ledger, profile_id, **body.model_dump(), actor=actor)

    @app.post("/api/localization/plan")
    def localization(body: LocalizationInput, actor=Actor, ledger=DB):
        from statement_ledger.application.acceleration import localize

        return localize(ledger, **body.model_dump(), actor=actor)

    @app.post("/api/localization/combine")
    def combine(body: WorkInput, actor=Actor, ledger=DB):
        from statement_ledger.pillars.speech.localization import combined_work

        return combined_work(ledger, body.run_ids)

    @app.post("/api/claims/search")
    def claim_search(body: ClaimSearchInput, actor=Actor, ledger=DB):
        from statement_ledger.pillars.claims.library import search_claims

        return search_claims(ledger, **body.model_dump())

    @app.get("/api/claims/cards/{card_id}")
    def claim_card(card_id: str, actor=Actor, ledger=DB):
        from statement_ledger.pillars.claims.library import card_status

        return card_status(ledger, ledger.store.get("claim_card", card_id))

    @app.post("/api/claims/match")
    def claim_match(body: ClaimMatchInput, actor=Actor, ledger=DB):
        from statement_ledger.application.acceleration import match_claims

        return match_claims(ledger, **body.model_dump(), actor=actor)

    @app.get("/api/acceleration/status")
    def acceleration_status(actor=Actor, ledger=DB):
        return {
            "version": "0.3.0",
            "jev_enabled": settings.jev_enabled,
            "model": settings.jev_model,
            "speaker_identity_automatic": False,
            "verdict_reuse_automatic": False,
            "provider_receipts": ledger.store.verify_provider_receipts(),
        }

    @app.get("/readyz")
    def ready():
        check = Store(path, journal_mode=settings.journal_mode)
        try:
            check.db.execute("SELECT 1 FROM heads LIMIT 1").fetchone()
            return {"ready": True}
        finally:
            check.close()

    from statement_ledger.application.handlers import handlers
    from statement_ledger.infrastructure.operations import OperationJournal
    from statement_ledger.infrastructure.queue import RuntimeQueue
    from statement_ledger.infrastructure.worker import input_check

    @app.get("/api/runtime/config")
    def runtime_config(actor=Actor):
        return {
            "settings": settings.model_dump(mode="json"),
            "execution_hash": settings.execution_hash(),
        }

    @app.get("/api/jobs")
    def jobs(actor=Actor, ledger=DB):
        return {"jobs": RuntimeQueue(ledger.store).list()}

    @app.post("/api/jobs")
    def enqueue(body: JobRequest, actor=Actor, ledger=DB):
        registered = handlers().get(body.handler)
        if registered is None or registered.capability != body.capability:
            raise ValueError("Unknown or incompatible handler")
        if body.config_sha256 != settings.execution_hash():
            raise ValueError("Execution configuration mismatch")
        input_check(ledger, body)
        registered.validate(ledger, body)
        return {"job_id": RuntimeQueue(ledger.store).submit(body), "state": "outbox_pending"}

    @app.post("/api/jobs/{job_id}/cancel")
    def cancel(job_id: str, actor=Actor, ledger=DB):
        queue = RuntimeQueue(ledger.store)
        queue.cancel(job_id)
        return queue.get(job_id)

    @app.get("/api/operations")
    def operations(actor=Actor, ledger=DB):
        return {"operations": OperationJournal(ledger.store).list()}

    return app
