---
id: SL-009
title: "Implement piecewise timeline alignment and occurrence clusters"
status: proposed
gate: G4
dependencies: ["SL-008"]
---

# SL-009: Implement piecewise timeline alignment and occurrence clusters

## Objective and boundaries

Replace single-offset-only deduplication with reviewed piecewise mappings and stable occurrence clusters for edited clips, inserted ads, speed shifts and differing transcript boundaries.

This work belongs only to this standalone repository. Do not copy application-specific contracts, source credentials or a canonical database from another product. The current delivery state is `proposed`; future acceptance criteria are not completed merely because they are written here.

## Acceptance criteria

- [ ] A three-cut compilation maps its retained spans to the correct original source intervals.
- [ ] Small legitimate segmentation changes do not create extra occurrences.
- [ ] Ambiguous mappings remain excluded until reviewed; cluster version changes recompute counts.

## Required adversarial case

Two copies differ by 300 ms in transcript segmentation and inflate counts.

## Implementation surfaces

- `src/statement_ledger/media.py`
- `src/statement_ledger/service.py`
- `tests/test_piecewise_alignment.py`

## Validation and completion evidence

Retain the exact command, environment, fixture or permitted source hash, result, and unresolved limitations. Mocked transport proves client behavior only; a source integration requires an authorized real fixture and bounded live proof. A model/throughput claim requires a real run. Add regression tests for both acceptance and refusal paths; regenerate affected schemas and specification before closing the ticket.

## Rollback

Keep the feature disabled until its gate passes. On regression, stop the new producer/consumer, preserve immutable record history and audit evidence, and restore the previously validated behavior. Do not erase conflicting evidence or reapprove stale descendants merely to recover green status.
