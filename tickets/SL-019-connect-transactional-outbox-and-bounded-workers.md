---
id: SL-019
title: "Connect transactional outbox and bounded workers"
status: proposed
gate: G6
dependencies: ["SL-003", "SL-010"]
---

# SL-019: Connect transactional outbox and bounded workers

## Objective and boundaries

Wire committed outbox events to idempotent workflow jobs with explicit stage transitions, retries, dead letters, lease fencing and graceful cancellation.

This work belongs only to this standalone repository. Do not copy application-specific contracts, source credentials or a canonical database from another product. The current delivery state is `proposed`; future acceptance criteria are not completed merely because they are written here.

## Acceptance criteria

- [ ] Crash between commit and dispatch is replayed safely.
- [ ] A stale worker cannot complete a newer lease or overwrite an updated source revision.
- [ ] A cancelled/expired job cannot publish or continue external transfers.

## Required adversarial case

Two workers run the same speech or publication action after a lease expires.

## Implementation surfaces

- `src/statement_ledger/jobs.py`
- `src/statement_ledger/workers.py`
- `tests/test_worker_replay.py`

## Validation and completion evidence

Retain the exact command, environment, fixture or permitted source hash, result, and unresolved limitations. Mocked transport proves client behavior only; a source integration requires an authorized real fixture and bounded live proof. A model/throughput claim requires a real run. Add regression tests for both acceptance and refusal paths; regenerate affected schemas and specification before closing the ticket.

## Rollback

Keep the feature disabled until its gate passes. On regression, stop the new producer/consumer, preserve immutable record history and audit evidence, and restore the previously validated behavior. Do not erase conflicting evidence or reapprove stale descendants merely to recover green status.
