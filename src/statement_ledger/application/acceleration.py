"""Application-level entry points shared by CLI and authenticated API."""

from __future__ import annotations

from statement_ledger.core.policy import PolicyError
from statement_ledger.infrastructure.providers.jev import JevClient, JevConfig, run_decision
from statement_ledger.pillars.claims.library import inspect_match, match_request
from statement_ledger.pillars.speech.localization import plan_localization, semantic_request


def configured_client(ledger=None):
    from statement_ledger.infrastructure.secrets import LocalSecrets
    from statement_ledger.infrastructure.settings import load_settings

    settings = getattr(ledger, "settings", None) or load_settings()
    if not settings.jev_enabled:
        raise PolicyError("Jev is disabled; set SL_ENABLE_JEV=1 to permit remote evaluation")
    key = LocalSecrets().value("TYPESAFE_API_KEY")
    client = JevClient(key, config=JevConfig(model=settings.jev_model, max_attempts=1))
    client.operation_policy = (settings.remote_estimate_micro_usd, settings.remote_budget_micro_usd)
    return client


def localize(
    ledger,
    profile_id,
    transcript_id,
    *,
    config=None,
    use_jev=False,
    max_calls=16,
    actor="local-operator",
    client=None,
):
    decision_ids = []
    cache_hits = 0
    issues = []
    if use_jev:
        batches, issues = semantic_request(
            ledger, profile_id, transcript_id, config, max_calls=max_calls
        )
        # Do not pay for a known-incomplete batch set; deterministic fallback records
        # why semantic acceleration was not attempted.
        if issues:
            fallback_config = {**(config or {}), "mode": "shadow"}
            row = plan_localization(
                ledger, profile_id, transcript_id, config=fallback_config, actor=actor
            )
            return {
                "run": row,
                "decision_run_ids": [],
                "cache_hits": 0,
                "semantic_status": "not_attempted",
                "warnings": issues,
            }
        owned = client is None
        if owned:
            client = configured_client(ledger)
        try:
            for batch in batches:
                result = run_decision(ledger, batch, client, actor=actor)
                decision_ids.append(result["record"]["id"])
                cache_hits += int(result["cache_hit"])
                if result["record"]["payload"]["status"] == "unavailable":
                    issues.append(result["record"]["payload"]["error_code"])
                    break
        finally:
            if owned:
                client.close()
    row = plan_localization(
        ledger, profile_id, transcript_id, config=config, decision_run_ids=decision_ids, actor=actor
    )
    return {
        "run": row,
        "decision_run_ids": decision_ids,
        "cache_hits": cache_hits,
        "semantic_status": "unavailable"
        if issues
        else "available"
        if decision_ids
        else "not_requested",
        "warnings": issues,
    }


def match_claims(ledger, proposition_id, candidate_ids, *, actor="local-operator", client=None):
    req = match_request(ledger, proposition_id, candidate_ids)
    owned = client is None
    if owned:
        client = configured_client(ledger)
    try:
        result = run_decision(ledger, req, client, actor=actor)
    finally:
        if owned:
            client.close()
    return {**inspect_match(ledger, result["record"]["id"]), "cache_hit": result["cache_hit"]}
