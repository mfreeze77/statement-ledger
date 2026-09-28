---
id: SL-214
title: "Fit and govern event-held-out localization calibration"
status: proposed
gate: G3
dependencies: ["SL-211", "SL-212", "SL-213"]
---

# SL-214: Fit and govern event-held-out localization calibration

## Scope and contract

Upgrade work for the standalone Statement Ledger application. Implementation surfaces: `evaluation/calibration/; calibration adapter`.
The status refers only to the named bounded scope; it does not close broader original source, production or real-model gates.

## Acceptance criteria

- [ ] Use training/validation/test events and retain each calibration artifact and feature version.
- [ ] Report calibration, uncertainty, recall and selected duration under domain shift.
- [ ] Require explicit promotion/rollback and keep shadow fallback for unknown domains.

## Required adversarial case

A low sample Brier score is used to claim universal speaker-probability calibration.

## Evidence and validation

Before closing, commit the exact executed command, environment/model revisions, authorized corpus hashes, measured results and refusal paths. Do not turn a mock or a synthetic fixture into a claimed real acceptance. Keep configuration disabled or shadow until this gate has evidence.

## Rollback

Disable the new producer or assist route, keep full-audio/manual review available, preserve revision history and raw failure receipts, and rebuild only approved derived indexes. Do not delete conflicting evidence or silently restore expired permissions.
