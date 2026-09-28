from __future__ import annotations

from statement_ledger.core.util import canonical_url


def validate_person(ledger, payload, ref):
    for url in payload["identity_urls"]:
        canonical_url(url)


def validate_rights(ledger, payload, ref):
    from statement_ledger.contracts.source_catalog import source

    source(payload["source_id"])
    if payload["evidence_url"]:
        canonical_url(payload["evidence_url"])
