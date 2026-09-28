---
id: SL-021
title: "Migrate canonical storage for multi-worker operation"
status: proposed
gate: G6
dependencies: ["SL-017", "SL-019"]
---

# SL-021: Migrate canonical storage for multi-worker operation

## Objective and boundaries

Design and implement a standalone PostgreSQL schema/migration only when measured concurrency or scale exceeds SQLite’s validated role. Preserve revision and dependency semantics.

This work belongs only to this standalone repository. Do not copy application-specific contracts, source credentials or a canonical database from another product. The current delivery state is `proposed`; future acceptance criteria are not completed merely because they are written here.

## Acceptance criteria

- [ ] Restore a known reference dataset with identical logical IDs, hashes and counts.
- [ ] Concurrent writes preserve expected-revision conflicts and outbox atomicity.
- [ ] Provide a tested rollback and backup recovery plan.

## Required adversarial case

Migration silently drops stale flags or accepts duplicate current heads.

## Implementation surfaces

- `migrations/`
- `src/statement_ledger/store.py`
- `tests/integration/`

## Validation and completion evidence

Retain the exact command, environment, fixture or permitted source hash, result, and unresolved limitations. Mocked transport proves client behavior only; a source integration requires an authorized real fixture and bounded live proof. A model/throughput claim requires a real run. Add regression tests for both acceptance and refusal paths; regenerate affected schemas and specification before closing the ticket.

## Rollback

Keep the feature disabled until its gate passes. On regression, stop the new producer/consumer, preserve immutable record history and audit evidence, and restore the previously validated behavior. Do not erase conflicting evidence or reapprove stale descendants merely to recover green status.
