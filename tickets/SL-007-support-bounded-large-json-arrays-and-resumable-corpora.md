---
id: SL-007
title: "Support bounded large JSON arrays and resumable corpora"
status: proposed
gate: G2
dependencies: ["SL-004"]
---

# SL-007: Support bounded large JSON arrays and resumable corpora

## Objective and boundaries

Add streaming root-array ingestion, durable checkpoints and stable row identities for authorized bulk datasets beyond the reference 64 MiB array limit.

This work belongs only to this standalone repository. Do not copy application-specific contracts, source credentials or a canonical database from another product. The current delivery state is `proposed`; future acceptance criteria are not completed merely because they are written here.

## Acceptance criteria

- [ ] Process a representative large compressed fixture with bounded resident memory.
- [ ] Restart at a validated checkpoint without changing stable IDs or silently losing rows.
- [ ] Malformed and oversized rows produce explicit quarantine receipts while preserving the declared import policy.

## Required adversarial case

The parser loads a multi-gigabyte root array in memory or restarts by creating duplicate records.

## Implementation surfaces

- `src/statement_ledger/ingest.py`
- `src/statement_ledger/connectors/parsers.py`
- `tests/test_large_ingest.py`

## Validation and completion evidence

Retain the exact command, environment, fixture or permitted source hash, result, and unresolved limitations. Mocked transport proves client behavior only; a source integration requires an authorized real fixture and bounded live proof. A model/throughput claim requires a real run. Add regression tests for both acceptance and refusal paths; regenerate affected schemas and specification before closing the ticket.

## Rollback

Keep the feature disabled until its gate passes. On regression, stop the new producer/consumer, preserve immutable record history and audit evidence, and restore the previously validated behavior. Do not erase conflicting evidence or reapprove stale descendants merely to recover green status.
