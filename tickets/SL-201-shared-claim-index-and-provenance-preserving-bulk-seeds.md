---
id: SL-201
title: "Shared claim index and provenance-preserving bulk seeds"
status: verified_local_reference
gate: G3
dependencies: ["SL-001"]
---

# SL-201: Shared claim index and provenance-preserving bulk seeds

## Scope and contract

Upgrade work for the standalone Statement Ledger application. Implementation surfaces: `claim_library.py; claim_seeds.py`.
The status refers only to the named bounded scope; it does not close broader original source, production or real-model gates.

## Acceptance criteria

- [x] Keep all seed rows as attributed leads; no imported finding becomes a review.
- [x] Index scoped propositions independently of a person and deduplicate only exact seed text/scope.
- [x] Preserve source observations, raw file hash, per-row failures and bounded completion state.

## Required adversarial case

An imported row supplies a finding field or a batch repeats the same source quote.

## Evidence and validation

Read `docs/VALIDATION_REPORT.md`, the relevant tests under `tests/test_acceleration*.py` and `tests/test_jev.py`, and generated contracts. Local/synthetic tests do not establish real-world accuracy. Mocked contract statuses explicitly do not establish a successful live provider call.

## Rollback

Disable the new producer or assist route, keep full-audio/manual review available, preserve revision history and raw failure receipts, and rebuild only approved derived indexes. Do not delete conflicting evidence or silently restore expired permissions.
