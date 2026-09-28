---
id: SL-029
title: "Add operational observability without source leakage"
status: proposed
gate: G6
dependencies: ["SL-019"]
---

# SL-029: Add operational observability without source leakage

## Objective and boundaries

Expose redacted metrics for connector health, parse quarantine, staleness, job age, rights blocks and review backlog. Keep content/credentials out of metrics labels.

This work belongs only to this standalone repository. Do not copy application-specific contracts, source credentials or a canonical database from another product. The current delivery state is `proposed`; future acceptance criteria are not completed merely because they are written here.

## Acceptance criteria

- [ ] Logs contain run IDs and bounded errors, not bearer tokens or complete source text.
- [ ] Alerts distinguish source outage from schema drift and local parser failure.
- [ ] Operators can trace one failed workflow without searching private content logs.

## Required adversarial case

A provider error embeds its URL query key and leaks the credential into telemetry.

## Implementation surfaces

- `src/statement_ledger/observability.py`
- `tests/test_redaction.py`

## Validation and completion evidence

Retain the exact command, environment, fixture or permitted source hash, result, and unresolved limitations. Mocked transport proves client behavior only; a source integration requires an authorized real fixture and bounded live proof. A model/throughput claim requires a real run. Add regression tests for both acceptance and refusal paths; regenerate affected schemas and specification before closing the ticket.

## Rollback

Keep the feature disabled until its gate passes. On regression, stop the new producer/consumer, preserve immutable record history and audit evidence, and restore the previously validated behavior. Do not erase conflicting evidence or reapprove stale descendants merely to recover green status.
