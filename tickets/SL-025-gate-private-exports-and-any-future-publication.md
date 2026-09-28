---
id: SL-025
title: "Gate private exports and any future publication"
status: blocked
gate: G7
dependencies: ["SL-016", "SL-017", "SL-023", "SL-026"]
---

# SL-025: Gate private exports and any future publication

## Objective and boundaries

Implement private reproducible evidence packs first; keep public views disabled until separate rights, security, evidence and editorial review gates pass.

This work belongs only to this standalone repository. Do not copy application-specific contracts, source credentials or a canonical database from another product. The current delivery state is `blocked`; future acceptance criteria are not completed merely because they are written here.

## Acceptance criteria

- [ ] Export contains only authorized exact source revisions and redacted secrets.
- [ ] Every consequential finding retains evidence, context, scope and correction links.
- [ ] Revoked/expired/stale records are blocked at export time, not just when originally approved.

## Required adversarial case

A public export includes restricted transcript text or a stale finding because it was once approved.

## Implementation surfaces

- `src/statement_ledger/exports.py`
- `docs/runbooks/`
- `tests/test_publication_gate.py`

## Validation and completion evidence

Retain the exact command, environment, fixture or permitted source hash, result, and unresolved limitations. Mocked transport proves client behavior only; a source integration requires an authorized real fixture and bounded live proof. A model/throughput claim requires a real run. Add regression tests for both acceptance and refusal paths; regenerate affected schemas and specification before closing the ticket.

## Rollback

Keep the feature disabled until its gate passes. On regression, stop the new producer/consumer, preserve immutable record history and audit evidence, and restore the previously validated behavior. Do not erase conflicting evidence or reapprove stale descendants merely to recover green status.
