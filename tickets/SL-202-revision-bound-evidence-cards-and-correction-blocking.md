---
id: SL-202
title: "Revision-bound evidence cards and correction blocking"
status: verified_local_reference
gate: G3
dependencies: ["SL-201"]
---

# SL-202: Revision-bound evidence cards and correction blocking

## Scope and contract

Upgrade work for the standalone Statement Ledger application. Implementation surfaces: `claim_library.py; service.py`.
The status refers only to the named bounded scope; it does not close broader original source, production or real-model gates.

## Acceptance criteria

- [x] Cards reference reviewed findings for one exact proposition and carry an explicit expiry.
- [x] Incomplete scope, stale ancestry, open corrections and conflicting findings block reuse.
- [x] Unrelated primary context cannot satisfy a factual primary-evidence relation.

## Required adversarial case

A context-only primary source is attached to an unsupported external verdict.

## Evidence and validation

Read `docs/VALIDATION_REPORT.md`, the relevant tests under `tests/test_acceleration*.py` and `tests/test_jev.py`, and generated contracts. Local/synthetic tests do not establish real-world accuracy. Mocked contract statuses explicitly do not establish a successful live provider call.

## Rollback

Disable the new producer or assist route, keep full-audio/manual review available, preserve revision history and raw failure receipts, and rebuild only approved derived indexes. Do not delete conflicting evidence or silently restore expired permissions.
