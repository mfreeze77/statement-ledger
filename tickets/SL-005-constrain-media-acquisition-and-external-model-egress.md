---
id: SL-005
title: "Constrain media acquisition and external-model egress"
status: proposed
gate: G2
dependencies: ["SL-003"]
---

# SL-005: Constrain media acquisition and external-model egress

## Objective and boundaries

Introduce reviewed acquisition manifests and an isolated bounded media-fetch worker for approved hosts and operations. Resolve redirects only under explicit origin/IP policy; refuse arbitrary source-text URLs.

This work belongs only to this standalone repository. Do not copy application-specific contracts, source credentials or a canonical database from another product. The current delivery state is `proposed`; future acceptance criteria are not completed merely because they are written here.

## Acceptance criteria

- [ ] Test localhost, metadata-service IPs, mixed DNS answers, redirects and oversized compressed responses.
- [ ] Before external model transfer, enforce a separate grant for sending source data to that provider.
- [ ] Denied acquisition leaves a visible source gap and does not try another unauthorized route.

## Required adversarial case

An article embeds an internal URL that a worker fetches with network access or credentials.

## Implementation surfaces

- `src/statement_ledger/acquisition.py`
- `src/statement_ledger/policy.py`
- `tests/test_acquisition.py`

## Validation and completion evidence

Retain the exact command, environment, fixture or permitted source hash, result, and unresolved limitations. Mocked transport proves client behavior only; a source integration requires an authorized real fixture and bounded live proof. A model/throughput claim requires a real run. Add regression tests for both acceptance and refusal paths; regenerate affected schemas and specification before closing the ticket.

## Rollback

Keep the feature disabled until its gate passes. On regression, stop the new producer/consumer, preserve immutable record history and audit evidence, and restore the previously validated behavior. Do not erase conflicting evidence or reapprove stale descendants merely to recover green status.
