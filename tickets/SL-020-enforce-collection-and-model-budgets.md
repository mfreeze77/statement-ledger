---
id: SL-020
title: "Enforce collection and model budgets"
status: proposed
gate: G6
dependencies: ["SL-019"]
---

# SL-020: Enforce collection and model budgets

## Objective and boundaries

Track provider requests, media minutes, bytes, model calls and reviewer effort against per-investigation budgets. Prices remain operator configuration, not remembered fixed facts.

This work belongs only to this standalone repository. Do not copy application-specific contracts, source credentials or a canonical database from another product. The current delivery state is `proposed`; future acceptance criteria are not completed merely because they are written here.

## Acceptance criteria

- [ ] Budget exhaustion stops new work and emits a resumable reason.
- [ ] Cached/replayed jobs do not create new paid calls unnecessarily.
- [ ] Cost reports separate estimated and observed costs plus third-party subscriptions.

## Required adversarial case

An agent recursively follows all appearance links without a crawl or spend limit.

## Implementation surfaces

- `src/statement_ledger/budgets.py`
- `src/statement_ledger/jobs.py`
- `tests/test_budgets.py`

## Validation and completion evidence

Retain the exact command, environment, fixture or permitted source hash, result, and unresolved limitations. Mocked transport proves client behavior only; a source integration requires an authorized real fixture and bounded live proof. A model/throughput claim requires a real run. Add regression tests for both acceptance and refusal paths; regenerate affected schemas and specification before closing the ticket.

## Rollback

Keep the feature disabled until its gate passes. On regression, stop the new producer/consumer, preserve immutable record history and audit evidence, and restore the previously validated behavior. Do not erase conflicting evidence or reapprove stale descendants merely to recover green status.
