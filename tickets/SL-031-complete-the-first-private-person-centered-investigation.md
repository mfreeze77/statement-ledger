---
id: SL-031
title: "Complete the first private person-centered investigation"
status: proposed
gate: G3
dependencies: ["SL-003", "SL-004", "SL-006", "SL-010", "SL-011", "SL-018", "SL-027"]
---

# SL-031: Complete the first private person-centered investigation

## Objective and boundaries

Run the first bounded real-person pilot without importing any fabricated statements or findings. Establish scope, trace at least one appearance from discovery to exact reviewed words and evidence, and preserve refusals.

This work belongs only to this standalone repository. Do not copy application-specific contracts, source credentials or a canonical database from another product. The current delivery state is `proposed`; future acceptance criteria are not completed merely because they are written here.

## Acceptance criteria

- [ ] The real subject seed begins with zero appearance/claim/finding records.
- [ ] A reviewer reproduces one accepted utterance and explains one rejected or uncertain candidate.
- [ ] The report lists source gaps, duplicate copies, reviewed assertions, corrections and all unresolved limitations.

## Required adversarial case

The pilot begins with a presumption that a named person must receive a negative finding.

## Implementation surfaces

- `docs/runbooks/FIRST_INVESTIGATION.md`
- `evaluation/pilot/`
- `proof/`

## Validation and completion evidence

Retain the exact command, environment, fixture or permitted source hash, result, and unresolved limitations. Mocked transport proves client behavior only; a source integration requires an authorized real fixture and bounded live proof. A model/throughput claim requires a real run. Add regression tests for both acceptance and refusal paths; regenerate affected schemas and specification before closing the ticket.

## Rollback

Keep the feature disabled until its gate passes. On regression, stop the new producer/consumer, preserve immutable record history and audit evidence, and restore the previously validated behavior. Do not erase conflicting evidence or reapprove stale descendants merely to recover green status.
