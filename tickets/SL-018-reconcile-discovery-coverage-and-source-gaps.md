---
id: SL-018
title: "Reconcile discovery coverage and source gaps"
status: proposed
gate: G3
dependencies: ["SL-003", "SL-004"]
---

# SL-018: Reconcile discovery coverage and source gaps

## Objective and boundaries

Produce query/source/date coverage matrices, acquisition gaps and processed-appearance inventory. Distinguish the monitored population from unknown total appearances.

This work belongs only to this standalone repository. Do not copy application-specific contracts, source credentials or a canonical database from another product. The current delivery state is `proposed`; future acceptance criteria are not completed merely because they are written here.

## Acceptance criteria

- [ ] Partial pagination and unavailable transcripts remain visible.
- [ ] Combine query-led and bounded program-inventory discovery without losing their selection bias.
- [ ] Finished query never displays as complete universe of appearances.

## Required adversarial case

No hits from a rate-limited source is reported as evidence the person never appeared.

## Implementation surfaces

- `src/statement_ledger/coverage.py`
- `src/statement_ledger/static/`
- `tests/test_coverage.py`

## Validation and completion evidence

Retain the exact command, environment, fixture or permitted source hash, result, and unresolved limitations. Mocked transport proves client behavior only; a source integration requires an authorized real fixture and bounded live proof. A model/throughput claim requires a real run. Add regression tests for both acceptance and refusal paths; regenerate affected schemas and specification before closing the ticket.

## Rollback

Keep the feature disabled until its gate passes. On regression, stop the new producer/consumer, preserve immutable record history and audit evidence, and restore the previously validated behavior. Do not erase conflicting evidence or reapprove stale descendants merely to recover green status.
