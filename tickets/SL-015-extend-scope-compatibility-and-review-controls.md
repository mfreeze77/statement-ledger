---
id: SL-015
title: "Extend scope compatibility and review controls"
status: proposed
gate: G5
dependencies: ["SL-014"]
---

# SL-015: Extend scope compatibility and review controls

## Objective and boundaries

Add structured units/periods/denominators/definitions and a review workbench. Distinguish mismatch, missing scope and evidence conflict without equating semantic similarity with applicability.

This work belongs only to this standalone repository. Do not copy application-specific contracts, source credentials or a canonical database from another product. The current delivery state is `proposed`; future acceptance criteria are not completed merely because they are written here.

## Acceptance criteria

- [ ] Hard negatives include different years, jurisdictions, nominal versus real values and authorized versus actual spending.
- [ ] A reviewer sees contrary evidence and limitations before completing a finding.
- [ ] Source revision or scope change makes dependent reviews stale.

## Required adversarial case

A review about a nationwide total is reused for a state per-person metric.

## Implementation surfaces

- `src/statement_ledger/policy.py`
- `src/statement_ledger/service.py`
- `src/statement_ledger/static/`

## Validation and completion evidence

Retain the exact command, environment, fixture or permitted source hash, result, and unresolved limitations. Mocked transport proves client behavior only; a source integration requires an authorized real fixture and bounded live proof. A model/throughput claim requires a real run. Add regression tests for both acceptance and refusal paths; regenerate affected schemas and specification before closing the ticket.

## Rollback

Keep the feature disabled until its gate passes. On regression, stop the new producer/consumer, preserve immutable record history and audit evidence, and restore the previously validated behavior. Do not erase conflicting evidence or reapprove stale descendants merely to recover green status.
