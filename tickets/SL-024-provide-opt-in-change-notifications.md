---
id: SL-024
title: "Provide opt-in change notifications"
status: proposed
gate: G6
dependencies: ["SL-017", "SL-019", "SL-023"]
---

# SL-024: Provide opt-in change notifications

## Objective and boundaries

Add opt-in notifications for new confirmed appearances, changed evidence and corrections. Deduplicate delivery by material event and revision, not repeated source copies.

This work belongs only to this standalone repository. Do not copy application-specific contracts, source credentials or a canonical database from another product. The current delivery state is `proposed`; future acceptance criteria are not completed merely because they are written here.

## Acceptance criteria

- [ ] Retries do not send duplicate notifications.
- [ ] A correction notification links both prior and current records.
- [ ] No external email/webhook is invoked without configured authorization and recipient settings.

## Required adversarial case

A copied clip triggers twenty identical new-claim alerts.

## Implementation surfaces

- `src/statement_ledger/notifications.py`
- `tests/test_notifications.py`

## Validation and completion evidence

Retain the exact command, environment, fixture or permitted source hash, result, and unresolved limitations. Mocked transport proves client behavior only; a source integration requires an authorized real fixture and bounded live proof. A model/throughput claim requires a real run. Add regression tests for both acceptance and refusal paths; regenerate affected schemas and specification before closing the ticket.

## Rollback

Keep the feature disabled until its gate passes. On regression, stop the new producer/consumer, preserve immutable record history and audit evidence, and restore the previously validated behavior. Do not erase conflicting evidence or reapprove stale descendants merely to recover green status.
