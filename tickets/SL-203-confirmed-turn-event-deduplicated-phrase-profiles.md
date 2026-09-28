---
id: SL-203
title: "Confirmed-turn event-deduplicated phrase profiles"
status: verified_local_reference
gate: G3
dependencies: ["SL-001"]
---

# SL-203: Confirmed-turn event-deduplicated phrase profiles

## Scope and contract

Upgrade work for the standalone Statement Ledger application. Implementation surfaces: `profiles.py; acceleration_models.py`.
The status refers only to the named bounded scope; it does not close broader original source, production or real-model gates.

## Acceptance criteria

- [x] Accept only current reviewed target turns and explicit non-target comparison turns with learn_profile permission.
- [x] Count phrase support by independent original event, not copies or repeated segments.
- [x] Reproduce positive opening/closing/phrase weights from source records.

## Required adversarial case

Twenty copied soundbites try to meet independent-event readiness.

## Evidence and validation

Read `docs/VALIDATION_REPORT.md`, the relevant tests under `tests/test_acceleration*.py` and `tests/test_jev.py`, and generated contracts. Local/synthetic tests do not establish real-world accuracy. Mocked contract statuses explicitly do not establish a successful live provider call.

## Rollback

Disable the new producer or assist route, keep full-audio/manual review available, preserve revision history and raw failure receipts, and rebuild only approved derived indexes. Do not delete conflicting evidence or silently restore expired permissions.
