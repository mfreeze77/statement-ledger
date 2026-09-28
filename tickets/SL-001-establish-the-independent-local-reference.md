---
id: SL-001
title: "Establish the independent local reference"
status: verified_local_reference
gate: G1
dependencies: []
---

# SL-001: Establish the independent local reference

## Objective and boundaries

Freeze the delivered schemas, synthetic fixtures, integrity invariants, authenticated local API and reference counting semantics. Keep the fictional demo separate from any real investigation.

This work belongs only to this standalone repository. Do not copy application-specific contracts, source credentials or a canonical database from another product. The current delivery state is `verified_local_reference`; future acceptance criteria are not completed merely because they are written here.

## Acceptance criteria

- [x] Run the complete included test suite and retain environment/result evidence.
- [x] Show the original/copy/repeat example produces three assets, two assertion occurrences and one proposition.
- [x] Verify no other application namespace, secret or database dependency enters the tree.

## Required adversarial case

A copied clip inflates independent assertions, or a source quote is accepted as a verified utterance.

## Implementation surfaces

- `src/statement_ledger/`
- `tests/`
- `proof/`

## Validation and completion evidence

Retain the exact command, environment, fixture or permitted source hash, result, and unresolved limitations. Mocked transport proves client behavior only; a source integration requires an authorized real fixture and bounded live proof. A model/throughput claim requires a real run. Add regression tests for both acceptance and refusal paths; regenerate affected schemas and specification before closing the ticket.

## Rollback

Keep the feature disabled until its gate passes. On regression, stop the new producer/consumer, preserve immutable record history and audit evidence, and restore the previously validated behavior. Do not erase conflicting evidence or reapprove stale descendants merely to recover green status.
