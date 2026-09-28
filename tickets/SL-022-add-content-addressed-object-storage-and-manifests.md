---
id: SL-022
title: "Add content-addressed object storage and manifests"
status: proposed
gate: G6
dependencies: ["SL-006", "SL-019"]
---

# SL-022: Add content-addressed object storage and manifests

## Objective and boundaries

Provide a generic private object store for raw files, media and derivatives with checksums, manifests and retention boundaries. Canonical records remain in the standalone ledger.

This work belongs only to this standalone repository. Do not copy application-specific contracts, source credentials or a canonical database from another product. The current delivery state is `proposed`; future acceptance criteria are not completed merely because they are written here.

## Acceptance criteria

- [ ] Checksum verification precedes processing and after restore.
- [ ] Object paths cannot reveal secrets or allow cross-workspace traversal.
- [ ] Database backups include a referenced-object inventory and missing-object detection.

## Required adversarial case

A stale presigned URL is stored as if it were a durable source artifact.

## Implementation surfaces

- `src/statement_ledger/object_store.py`
- `docs/runbooks/`
- `tests/integration/`

## Validation and completion evidence

Retain the exact command, environment, fixture or permitted source hash, result, and unresolved limitations. Mocked transport proves client behavior only; a source integration requires an authorized real fixture and bounded live proof. A model/throughput claim requires a real run. Add regression tests for both acceptance and refusal paths; regenerate affected schemas and specification before closing the ticket.

## Rollback

Keep the feature disabled until its gate passes. On regression, stop the new producer/consumer, preserve immutable record history and audit evidence, and restore the previously validated behavior. Do not erase conflicting evidence or reapprove stale descendants merely to recover green status.
