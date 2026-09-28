---
id: SL-017
title: "Version ledger snapshots and counting policies"
status: proposed
gate: G4
dependencies: ["SL-009", "SL-016"]
---

# SL-017: Version ledger snapshots and counting policies

## Objective and boundaries

Materialize reproducible subject ledger snapshots with explicit inclusion/exclusion policy, cluster versions, reviewed proposition counts, repetitions and correction treatment.

This work belongs only to this standalone repository. Do not copy application-specific contracts, source credentials or a canonical database from another product. The current delivery state is `proposed`; future acceptance criteria are not completed merely because they are written here.

## Acceptance criteria

- [ ] Every displayed aggregate drills down to its exact contributing records and revisions.
- [ ] Unresolved identity/alignment, stale evidence and unreviewed extraction are listed as exclusions.
- [ ] No aggregate is presented as a person’s universal truthfulness, intent or character.

## Required adversarial case

Counts change after source updates without a new snapshot/policy version or explanation.

## Implementation surfaces

- `src/statement_ledger/counts.py`
- `contracts/`
- `tests/test_snapshot_counts.py`

## Validation and completion evidence

Retain the exact command, environment, fixture or permitted source hash, result, and unresolved limitations. Mocked transport proves client behavior only; a source integration requires an authorized real fixture and bounded live proof. A model/throughput claim requires a real run. Add regression tests for both acceptance and refusal paths; regenerate affected schemas and specification before closing the ticket.

## Rollback

Keep the feature disabled until its gate passes. On regression, stop the new producer/consumer, preserve immutable record history and audit evidence, and restore the previously validated behavior. Do not erase conflicting evidence or reapprove stale descendants merely to recover green status.
