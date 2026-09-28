from __future__ import annotations

from statement_ledger.contracts.models import RightsGrant
from statement_ledger.core.policy import PolicyError, require_right
from statement_ledger.core.util import canonical_url


def validate_asset(ledger, payload, ref):
    ref("event", payload["event_id"])
    obs = ref("observation", payload["observation_id"])
    grant = RightsGrant.model_validate(ref("rights", payload["rights_id"]))
    require_right(grant, "discover", obs["source_id"])
    canonical_url(payload["url"])
    if payload["event_offset_ms"] is not None and type(payload["event_offset_ms"]) is not int:
        raise PolicyError("Event offset must be integer milliseconds")
