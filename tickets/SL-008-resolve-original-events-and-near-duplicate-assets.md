---
id: SL-008
title: "Resolve original events and near-duplicate assets"
status: proposed
gate: G4
dependencies: ["SL-004"]
---

# SL-008: Resolve original events and near-duplicate assets

## Objective and boundaries

Generate original/copy candidate groups from source links, transcript similarity and approved media fingerprints. Store uncertain alternatives and require evidence before merging event identity.

This work belongs only to this standalone repository. Do not copy application-specific contracts, source credentials or a canonical database from another product. The current delivery state is `proposed`; future acceptance criteria are not completed merely because they are written here.

## Acceptance criteria

- [ ] Same recording re-encoded at a different bitrate is a candidate copy.
- [ ] Two separate interviews with nearly identical wording remain distinct events.
- [ ] Merge and split operations retain lineage and invalidate dependent occurrence groups.

## Required adversarial case

Text similarity alone merges two independent appearances and loses a repeat assertion.

## Implementation surfaces

- `src/statement_ledger/event_resolution.py`
- `src/statement_ledger/models.py`
- `tests/test_event_resolution.py`

## Validation and completion evidence

Retain the exact command, environment, fixture or permitted source hash, result, and unresolved limitations. Mocked transport proves client behavior only; a source integration requires an authorized real fixture and bounded live proof. A model/throughput claim requires a real run. Add regression tests for both acceptance and refusal paths; regenerate affected schemas and specification before closing the ticket.

## Rollback

Keep the feature disabled until its gate passes. On regression, stop the new producer/consumer, preserve immutable record history and audit evidence, and restore the previously validated behavior. Do not erase conflicting evidence or reapprove stale descendants merely to recover green status.
