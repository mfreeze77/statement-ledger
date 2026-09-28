---
id: SL-006
title: "Add asset-scoped rights and retention inheritance"
status: proposed
gate: G2
dependencies: ["SL-003"]
---

# SL-006: Add asset-scoped rights and retention inheritance

## Objective and boundaries

Extend source-level grants to dataset, asset and operation scopes. Track contract revision, permission conflicts, expiry and derivative inheritance without treating source-level permission as universal.

This work belongs only to this standalone repository. Do not copy application-specific contracts, source credentials or a canonical database from another product. The current delivery state is `proposed`; future acceptance criteria are not completed merely because they are written here.

## Acceptance criteria

- [ ] A grant for one recording cannot authorize another recording from the same source.
- [ ] Derivatives inherit applicable retention and redistribution constraints.
- [ ] Conflicting or missing permissions fail closed with an operator explanation.

## Required adversarial case

A synthetic grant or broad source label accidentally authorizes a real recording.

## Implementation surfaces

- `src/statement_ledger/models.py`
- `src/statement_ledger/policy.py`
- `docs/runbooks/RIGHTS_AND_CORRECTIONS.md`

## Validation and completion evidence

Retain the exact command, environment, fixture or permitted source hash, result, and unresolved limitations. Mocked transport proves client behavior only; a source integration requires an authorized real fixture and bounded live proof. A model/throughput claim requires a real run. Add regression tests for both acceptance and refusal paths; regenerate affected schemas and specification before closing the ticket.

## Rollback

Keep the feature disabled until its gate passes. On regression, stop the new producer/consumer, preserve immutable record history and audit evidence, and restore the previously validated behavior. Do not erase conflicting evidence or reapprove stale descendants merely to recover green status.
