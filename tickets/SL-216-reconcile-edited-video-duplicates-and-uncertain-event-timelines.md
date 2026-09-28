---
id: SL-216
title: "Reconcile edited-video duplicates and uncertain event timelines"
status: proposed
gate: G3
dependencies: ["SL-008", "SL-009", "SL-205"]
---

# SL-216: Reconcile edited-video duplicates and uncertain event timelines

## Scope and contract

Upgrade work for the standalone Statement Ledger application. Implementation surfaces: `media matching; occurrence reconciliation`.
The status refers only to the named bounded scope; it does not close broader original source, production or real-model gates.

## Acceptance criteria

- [ ] Implement verified piecewise mappings for excerpts and nonlinear compilations.
- [ ] Do not count uploads as independent events; make merge reversal rebuild derived counts.
- [ ] Preserve uncertain alignment rather than forcing the same words onto one timeline.

## Required adversarial case

A compilation reorders excerpts or contains the same soundbite twice.

## Evidence and validation

Before closing, commit the exact executed command, environment/model revisions, authorized corpus hashes, measured results and refusal paths. Do not turn a mock or a synthetic fixture into a claimed real acceptance. Keep configuration disabled or shadow until this gate has evidence.

## Rollback

Disable the new producer or assist route, keep full-audio/manual review available, preserve revision history and raw failure receipts, and rebuild only approved derived indexes. Do not delete conflicting evidence or silently restore expired permissions.
