---
id: SL-218
title: "Complete real browser validation and collaborative review UX"
status: proposed
gate: G3
dependencies: ["SL-205", "SL-202"]
---

# SL-218: Complete real browser validation and collaborative review UX

## Scope and contract

Upgrade work for the standalone Statement Ledger application. Implementation surfaces: `static/; api.py; browser tests`.
The status refers only to the named bounded scope; it does not close broader original source, production or real-model gates.

## Acceptance criteria

- [ ] Run real browser navigation, keyboard interaction and failure-state checks in an allowed environment.
- [ ] Add review flows without exposing provider credentials or unapproved public findings.
- [ ] Bind server-authenticated reviewer principals before any multi-user deployment.

## Required adversarial case

A client supplies an arbitrary reviewer name to approve another user's finding.

## Evidence and validation

Before closing, commit the exact executed command, environment/model revisions, authorized corpus hashes, measured results and refusal paths. Do not turn a mock or a synthetic fixture into a claimed real acceptance. Keep configuration disabled or shadow until this gate has evidence.

## Rollback

Disable the new producer or assist route, keep full-audio/manual review available, preserve revision history and raw failure receipts, and rebuild only approved derived indexes. Do not delete conflicting evidence or silently restore expired permissions.
