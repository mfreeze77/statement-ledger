from __future__ import annotations

from statement_ledger.contracts.models import RightsGrant
from statement_ledger.core.policy import PolicyError, require_right
from statement_ledger.core.util import canonical_url, digest


def validate_observation(ledger, payload, ref):
    from statement_ledger.contracts.source_catalog import source

    source(payload["source_id"])
    grant = RightsGrant.model_validate(ref("rights", payload["rights_id"]))
    require_right(grant, "store_text", payload["source_id"])
    canonical_url(payload["url"])
    for url in payload["links"]:
        canonical_url(url)
    if digest(payload["raw_payload"]) != payload["raw_sha256"]:
        raise PolicyError("Raw payload checksum does not match")


def validate_event(ledger, payload, ref):
    for oid in payload["observation_ids"]:
        ref("observation", oid)


def validate_appearance(ledger, payload, ref):
    ref("event", payload["event_id"])
    ref("person", payload["person_id"])
    for oid in payload["observation_ids"]:
        ref("observation", oid)


def validate_coverage_run(ledger, payload, ref):
    ref("person", payload["person_id"])
    from statement_ledger.contracts.source_catalog import source

    source(payload["source_id"])
    if payload["processed"] > payload["retrieved"]:
        raise PolicyError("Processed count exceeds retrieved count")
    if payload["period_end"] < payload["period_start"]:
        raise PolicyError("Coverage end precedes start")
