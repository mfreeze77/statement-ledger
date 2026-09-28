---
id: SL-013
title: "Add constrained candidate claim extraction"
status: proposed
gate: G5
dependencies: ["SL-012"]
---

# SL-013: Add constrained candidate claim extraction

## Objective and boundaries

Introduce a provider-neutral model port that proposes scoped propositions and assertion modes from accepted source contexts. Preserve exact text independently of paraphrases.

This work belongs only to this standalone repository. Do not copy application-specific contracts, source credentials or a canonical database from another product. The current delivery state is `proposed`; future acceptance criteria are not completed merely because they are written here.

## Acceptance criteria

- [ ] Validate structured outputs and require exact source references.
- [ ] Test quotations, denials, questions, conditionals, predictions and mixed claims.
- [ ] Models cannot approve a claim review, invent evidence or use subject reputation as truth evidence.

## Required adversarial case

The phrase “they said X, but that is wrong” is classified as an assertion of X.

## Implementation surfaces

- `src/statement_ledger/claims.py`
- `contracts/`
- `tests/test_claim_extraction.py`

## Validation and completion evidence

Retain the exact command, environment, fixture or permitted source hash, result, and unresolved limitations. Mocked transport proves client behavior only; a source integration requires an authorized real fixture and bounded live proof. A model/throughput claim requires a real run. Add regression tests for both acceptance and refusal paths; regenerate affected schemas and specification before closing the ticket.

## Rollback

Keep the feature disabled until its gate passes. On regression, stop the new producer/consumer, preserve immutable record history and audit evidence, and restore the previously validated behavior. Do not erase conflicting evidence or reapprove stale descendants merely to recover green status.
