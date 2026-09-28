---
id: SL-209
title: "Coverage diagnostics and full-cost comparison tools"
status: verified_local_reference
gate: G3
dependencies: ["SL-205"]
---

# SL-209: Coverage diagnostics and full-cost comparison tools

## Scope and contract

Upgrade work for the standalone Statement Ledger application. Implementation surfaces: `evaluation.py; cli.py`.
The status refers only to the named bounded scope; it does not close broader original source, production or real-model gates.

## Acceptance criteria

- [x] Keep time coverage and turn coverage separate with original event holdouts.
- [x] Empty target labels return undefined recall, not successful absence detection.
- [x] Calibration output is diagnostic only and prices are operator-supplied assumptions.

## Required adversarial case

Adjacent gold turns collapse into one interval or screening costs exceed saved audio work.

## Evidence and validation

Read `docs/VALIDATION_REPORT.md`, the relevant tests under `tests/test_acceleration*.py` and `tests/test_jev.py`, and generated contracts. Local/synthetic tests do not establish real-world accuracy. Mocked contract statuses explicitly do not establish a successful live provider call.

## Rollback

Disable the new producer or assist route, keep full-audio/manual review available, preserve revision history and raw failure receipts, and rebuild only approved derived indexes. Do not delete conflicting evidence or silently restore expired permissions.
