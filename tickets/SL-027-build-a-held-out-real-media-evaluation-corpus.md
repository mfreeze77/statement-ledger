---
id: SL-027
title: "Build a held-out real-media evaluation corpus"
status: proposed
gate: G3
dependencies: ["SL-010", "SL-011", "SL-018"]
---

# SL-027: Build a held-out real-media evaluation corpus

## Objective and boundaries

Assemble permitted, human-annotated examples and hard negatives held out by event/program/date. Define metrics and abstention accounting before evaluating the pipeline.

This work belongs only to this standalone repository. Do not copy application-specific contracts, source credentials or a canonical database from another product. The current delivery state is `proposed`; future acceptance criteria are not completed merely because they are written here.

## Acceptance criteria

- [ ] Separate identity precision, turn boundaries, ASR errors, scope compatibility and evidence support metrics.
- [ ] Include absent subject, overlap, quoted speech, edits, repeats and unknown dates.
- [ ] Publish internal acceptance thresholds as proposals until measured, never fabricated benchmark results.

## Required adversarial case

Train and test on different uploads of the same appearance and report inflated accuracy.

## Implementation surfaces

- `evaluation/`
- `tests/evaluation/`
- `docs/evaluation/`

## Validation and completion evidence

Retain the exact command, environment, fixture or permitted source hash, result, and unresolved limitations. Mocked transport proves client behavior only; a source integration requires an authorized real fixture and bounded live proof. A model/throughput claim requires a real run. Add regression tests for both acceptance and refusal paths; regenerate affected schemas and specification before closing the ticket.

## Rollback

Keep the feature disabled until its gate passes. On regression, stop the new producer/consumer, preserve immutable record history and audit evidence, and restore the previously validated behavior. Do not erase conflicting evidence or reapprove stale descendants merely to recover green status.
