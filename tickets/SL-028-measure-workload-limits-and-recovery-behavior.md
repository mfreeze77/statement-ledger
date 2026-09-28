---
id: SL-028
title: "Measure workload limits and recovery behavior"
status: proposed
gate: G6
dependencies: ["SL-019", "SL-021", "SL-022"]
---

# SL-028: Measure workload limits and recovery behavior

## Objective and boundaries

Run bounded load tests on the actual target deployment. Measure ingestion throughput, query latency, concurrent reviewer writes, processing backlog and restore time.

This work belongs only to this standalone repository. Do not copy application-specific contracts, source credentials or a canonical database from another product. The current delivery state is `proposed`; future acceptance criteria are not completed merely because they are written here.

## Acceptance criteria

- [ ] Record hardware, dataset shape and p50/p95/p99 rather than general claims.
- [ ] Simulate disk full, timeouts, worker crashes and missing objects.
- [ ] Define and prove actual recovery objectives with a disposable restore.

## Required adversarial case

Synthetic unit-test duration is presented as a million-record production throughput claim.

## Implementation surfaces

- `benchmarks/`
- `docs/runbooks/`
- `proof/`

## Validation and completion evidence

Retain the exact command, environment, fixture or permitted source hash, result, and unresolved limitations. Mocked transport proves client behavior only; a source integration requires an authorized real fixture and bounded live proof. A model/throughput claim requires a real run. Add regression tests for both acceptance and refusal paths; regenerate affected schemas and specification before closing the ticket.

## Rollback

Keep the feature disabled until its gate passes. On regression, stop the new producer/consumer, preserve immutable record history and audit evidence, and restore the previously validated behavior. Do not erase conflicting evidence or reapprove stale descendants merely to recover green status.
