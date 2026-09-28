---
id: SL-030
title: "Harden packaging and release reproducibility"
status: proposed
gate: G6
dependencies: ["SL-002", "SL-028"]
---

# SL-030: Harden packaging and release reproducibility

## Objective and boundaries

Create signed/reproducible release inputs, validated dependency locks, generated contracts, container proofs and documented rollback on the chosen platform.

This work belongs only to this standalone repository. Do not copy application-specific contracts, source credentials or a canonical database from another product. The current delivery state is `proposed`; future acceptance criteria are not completed merely because they are written here.

## Acceptance criteria

- [ ] Clean CI rebuild validates schema/spec drift and standalone isolation.
- [ ] Release archive excludes real research media, tokens, local databases and caches.
- [ ] A separate machine can install, seed synthetic data, inspect the ledger and restore backup.

## Required adversarial case

A source ZIP contains an active research database or is accidentally published into a parent repository.

## Implementation surfaces

- `.github/workflows/`
- `scripts/`
- `proof/`
- `docs/VALIDATION_REPORT.md`

## Validation and completion evidence

Retain the exact command, environment, fixture or permitted source hash, result, and unresolved limitations. Mocked transport proves client behavior only; a source integration requires an authorized real fixture and bounded live proof. A model/throughput claim requires a real run. Add regression tests for both acceptance and refusal paths; regenerate affected schemas and specification before closing the ticket.

## Rollback

Keep the feature disabled until its gate passes. On regression, stop the new producer/consumer, preserve immutable record history and audit evidence, and restore the previously validated behavior. Do not erase conflicting evidence or reapprove stale descendants merely to recover green status.
