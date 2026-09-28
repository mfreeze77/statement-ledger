---
id: SL-205
title: "Caption window planner and shared audio interval unions"
status: verified_local_reference
gate: G3
dependencies: ["SL-203"]
---

# SL-205: Caption window planner and shared audio interval unions

## Scope and contract

Upgrade work for the standalone Statement Ledger application. Implementation surfaces: `localization.py; intervals.py`.
The status refers only to the named bounded scope; it does not close broader original source, production or real-model gates.

## Acceptance criteria

- [x] Default shadow processing covers the complete asset while retaining proposed windows.
- [x] Assist merges padded positives, reproducible audits and caption gaps.
- [x] Cold start, incomplete semantic batches and faults route to complete processing.
- [x] Combined person plans count audio union once without crossing asset timebases.

## Required adversarial case

The target makes a brief atypical interjection between captioned spans.

## Evidence and validation

Read `docs/VALIDATION_REPORT.md`, the relevant tests under `tests/test_acceleration*.py` and `tests/test_jev.py`, and generated contracts. Local/synthetic tests do not establish real-world accuracy. Mocked contract statuses explicitly do not establish a successful live provider call.

## Rollback

Disable the new producer or assist route, keep full-audio/manual review available, preserve revision history and raw failure receipts, and rebuild only approved derived indexes. Do not delete conflicting evidence or silently restore expired permissions.
