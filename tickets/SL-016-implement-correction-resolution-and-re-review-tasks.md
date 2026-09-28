---
id: SL-016
title: "Implement correction resolution and re-review tasks"
status: proposed
gate: G5
dependencies: ["SL-015"]
---

# SL-016: Implement correction resolution and re-review tasks

## Objective and boundaries

Connect reported corrections to explicit target revision, affected-dependency analysis, reassessment tasks and resolved/withdrawn outcomes. Keep correction records separate from the modified evidence.

This work belongs only to this standalone repository. Do not copy application-specific contracts, source credentials or a canonical database from another product. The current delivery state is `proposed`; future acceptance criteria are not completed merely because they are written here.

## Acceptance criteria

- [ ] A verified transcript correction identifies every affected occurrence and review.
- [ ] Historical and current states can both be reproduced.
- [ ] Creating a correction record alone does not falsely claim the target has been repaired.

## Required adversarial case

A correction for a different proposition is attached by name similarity and erases the original record.

## Implementation surfaces

- `src/statement_ledger/corrections.py`
- `src/statement_ledger/service.py`
- `tests/test_correction_workflow.py`

## Validation and completion evidence

Retain the exact command, environment, fixture or permitted source hash, result, and unresolved limitations. Mocked transport proves client behavior only; a source integration requires an authorized real fixture and bounded live proof. A model/throughput claim requires a real run. Add regression tests for both acceptance and refusal paths; regenerate affected schemas and specification before closing the ticket.

## Rollback

Keep the feature disabled until its gate passes. On regression, stop the new producer/consumer, preserve immutable record history and audit evidence, and restore the previously validated behavior. Do not erase conflicting evidence or reapprove stale descendants merely to recover green status.
