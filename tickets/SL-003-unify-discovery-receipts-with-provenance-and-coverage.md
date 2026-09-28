---
id: SL-003
title: "Unify discovery receipts with provenance and coverage"
status: proposed
gate: G2
dependencies: ["SL-001"]
---

# SL-003: Unify discovery receipts with provenance and coverage

## Objective and boundaries

Persist each discovery run, query, selected source contract, page cursor, redacted response reference and source authorization in the same research workflow. Replace the current separate response-file workflow with auditable run reconciliation.

This work belongs only to this standalone repository. Do not copy application-specific contracts, source credentials or a canonical database from another product. The current delivery state is `proposed`; future acceptance criteria are not completed merely because they are written here.

## Acceptance criteria

- [ ] Crashes between response retention and observation insertion are replayable without duplicate observations.
- [ ] An empty response, denied access, page-budget stop and parser failure remain distinct run outcomes.
- [ ] All retained query outputs link to approved grants and exact raw checksums.

## Required adversarial case

A failed source request silently appears as zero appearances and complete coverage.

## Implementation surfaces

- `src/statement_ledger/cli.py`
- `src/statement_ledger/ingest.py`
- `src/statement_ledger/models.py`
- `tests/test_discovery_runs.py`

## Validation and completion evidence

Retain the exact command, environment, fixture or permitted source hash, result, and unresolved limitations. Mocked transport proves client behavior only; a source integration requires an authorized real fixture and bounded live proof. A model/throughput claim requires a real run. Add regression tests for both acceptance and refusal paths; regenerate affected schemas and specification before closing the ticket.

## Rollback

Keep the feature disabled until its gate passes. On regression, stop the new producer/consumer, preserve immutable record history and audit evidence, and restore the previously validated behavior. Do not erase conflicting evidence or reapprove stale descendants merely to recover green status.
