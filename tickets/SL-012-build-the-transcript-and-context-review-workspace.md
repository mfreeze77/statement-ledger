---
id: SL-012
title: "Build the transcript and context review workspace"
status: proposed
gate: G3
dependencies: ["SL-010", "SL-011"]
---

# SL-012: Build the transcript and context review workspace

## Objective and boundaries

Extend the read-oriented inspector with source-aligned playback, selected turn boundaries, context expansion, transcript revision forms and speaker-evidence review.

This work belongs only to this standalone repository. Do not copy application-specific contracts, source credentials or a canonical database from another product. The current delivery state is `proposed`; future acceptance criteria are not completed merely because they are written here.

## Acceptance criteria

- [ ] A reviewer can inspect the prior question and later qualification before acceptance.
- [ ] All writes use optimistic revision checks and show conflicts rather than overwriting.
- [ ] Keyboard navigation and accessible status labels work without color alone.

## Required adversarial case

A transcript edit leaves an accepted utterance pointing to words that no longer exist.

## Implementation surfaces

- `src/statement_ledger/static/`
- `src/statement_ledger/api.py`
- `tests/browser/`

## Validation and completion evidence

Retain the exact command, environment, fixture or permitted source hash, result, and unresolved limitations. Mocked transport proves client behavior only; a source integration requires an authorized real fixture and bounded live proof. A model/throughput claim requires a real run. Add regression tests for both acceptance and refusal paths; regenerate affected schemas and specification before closing the ticket.

## Rollback

Keep the feature disabled until its gate passes. On regression, stop the new producer/consumer, preserve immutable record history and audit evidence, and restore the previously validated behavior. Do not erase conflicting evidence or reapprove stale descendants merely to recover green status.
