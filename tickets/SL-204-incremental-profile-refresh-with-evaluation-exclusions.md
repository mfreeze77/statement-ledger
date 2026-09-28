---
id: SL-204
title: "Incremental profile refresh with evaluation exclusions"
status: verified_local_reference
gate: G3
dependencies: ["SL-203"]
---

# SL-204: Incremental profile refresh with evaluation exclusions

## Scope and contract

Upgrade work for the standalone Statement Ledger application. Implementation surfaces: `profiles.py; cli.py; api.py`.
The status refers only to the named bounded scope; it does not close broader original source, production or real-model gates.

## Acceptance criteria

- [x] Refresh only from currently accepted target records and curated background speakers.
- [x] Exclude supplied holdout events and report skipped stale or unauthorized examples.
- [x] Preserve a new profile revision and invalidate dependent artifacts.

## Required adversarial case

A previously accepted training turn becomes stale after an attribution correction.

## Evidence and validation

Read `docs/VALIDATION_REPORT.md`, the relevant tests under `tests/test_acceleration*.py` and `tests/test_jev.py`, and generated contracts. Local/synthetic tests do not establish real-world accuracy. Mocked contract statuses explicitly do not establish a successful live provider call.

## Rollback

Disable the new producer or assist route, keep full-audio/manual review available, preserve revision history and raw failure receipts, and rebuild only approved derived indexes. Do not delete conflicting evidence or silently restore expired permissions.
