---
id: SL-210
title: "Additive database migration and release artifact proof"
status: verified_local_reference
gate: G3
dependencies: ["SL-201", "SL-207"]
---

# SL-210: Additive database migration and release artifact proof

## Scope and contract

Upgrade work for the standalone Statement Ledger application. Implementation surfaces: `store.py; scripts/; validation/`.
The status refers only to the named bounded scope; it does not close broader original source, production or real-model gates.

## Acceptance criteria

- [x] Add FTS/receipts without rewriting original stored payloads or hashes.
- [x] Export matching schemas/OpenAPI and independently run the delivered artifact.
- [x] Keep secrets, corpora, databases, models, temporary environments and other projects out of archives.

## Required adversarial case

An old proposition lacks newly introduced scope fields and must remain unchanged.

## Evidence and validation

Read `docs/VALIDATION_REPORT.md`, the relevant tests under `tests/test_acceleration*.py` and `tests/test_jev.py`, and generated contracts. Local/synthetic tests do not establish real-world accuracy. Mocked contract statuses explicitly do not establish a successful live provider call.

## Rollback

Disable the new producer or assist route, keep full-audio/manual review available, preserve revision history and raw failure receipts, and rebuild only approved derived indexes. Do not delete conflicting evidence or silently restore expired permissions.
