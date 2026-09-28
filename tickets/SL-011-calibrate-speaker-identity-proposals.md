---
id: SL-011
title: "Calibrate speaker identity proposals"
status: proposed
gate: G3
dependencies: ["SL-010"]
---

# SL-011: Calibrate speaker identity proposals

## Objective and boundaries

Build evidence-backed candidate identity proposals from explicit transcript labels, introductions and approved voice references. Keep unconfirmed and absent-subject cases in the evaluation set.

This work belongs only to this standalone repository. Do not copy application-specific contracts, source credentials or a canonical database from another product. The current delivery state is `proposed`; future acceptance criteria are not completed merely because they are written here.

## Acceptance criteria

- [ ] Recording-local labels never leak confirmed identity across recordings.
- [ ] Measure false matches separately from abstentions and incorrect segment boundaries.
- [ ] Human confirmation retains precise supporting evidence and rejected candidates.

## Required adversarial case

A lower-third or reused speaker_0 label names the wrong person.

## Implementation surfaces

- `src/statement_ledger/identity.py`
- `src/statement_ledger/models.py`
- `tests/test_identity.py`

## Validation and completion evidence

Retain the exact command, environment, fixture or permitted source hash, result, and unresolved limitations. Mocked transport proves client behavior only; a source integration requires an authorized real fixture and bounded live proof. A model/throughput claim requires a real run. Add regression tests for both acceptance and refusal paths; regenerate affected schemas and specification before closing the ticket.

## Rollback

Keep the feature disabled until its gate passes. On regression, stop the new producer/consumer, preserve immutable record history and audit evidence, and restore the previously validated behavior. Do not erase conflicting evidence or reapprove stale descendants merely to recover green status.
