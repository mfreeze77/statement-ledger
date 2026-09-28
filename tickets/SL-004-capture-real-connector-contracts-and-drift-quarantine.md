---
id: SL-004
title: "Capture real connector contracts and drift quarantine"
status: proposed
gate: G2
dependencies: ["SL-003"]
---

# SL-004: Capture real connector contracts and drift quarantine

## Objective and boundaries

For each activated source, save a permitted redacted real fixture and expected field mapping; compare future payload shapes against a versioned compatibility rule.

This work belongs only to this standalone repository. Do not copy application-specific contracts, source credentials or a canonical database from another product. The current delivery state is `proposed`; future acceptance criteria are not completed merely because they are written here.

## Acceptance criteria

- [ ] Unknown required shape enters quarantine rather than a zero-result success.
- [ ] Fixture distinguishes provider event date from upload/collection date.
- [ ] One actual bounded source response passes the parser and its refusal cases.

## Required adversarial case

A provider renames its records array and the adapter reports a successful empty collection.

## Implementation surfaces

- `src/statement_ledger/connectors/`
- `fixtures/`
- `docs/sources/`

## Validation and completion evidence

Retain the exact command, environment, fixture or permitted source hash, result, and unresolved limitations. Mocked transport proves client behavior only; a source integration requires an authorized real fixture and bounded live proof. A model/throughput claim requires a real run. Add regression tests for both acceptance and refusal paths; regenerate affected schemas and specification before closing the ticket.

## Rollback

Keep the feature disabled until its gate passes. On regression, stop the new producer/consumer, preserve immutable record history and audit evidence, and restore the previously validated behavior. Do not erase conflicting evidence or reapprove stale descendants merely to recover green status.
