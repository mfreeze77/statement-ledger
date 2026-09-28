---
id: SL-023
title: "Introduce production identities and authorization"
status: proposed
gate: G6
dependencies: ["SL-021"]
---

# SL-023: Introduce production identities and authorization

## Objective and boundaries

Replace the single-owner token with standalone role-based identities, sessions and trusted actor mapping if multiple users are introduced. Keep read, annotate, review, rights-admin and publication roles separate.

This work belongs only to this standalone repository. Do not copy application-specific contracts, source credentials or a canonical database from another product. The current delivery state is `proposed`; future acceptance criteria are not completed merely because they are written here.

## Acceptance criteria

- [ ] Direct ID requests cannot bypass workspace/object authorization.
- [ ] Caller-supplied reviewer or actor names cannot impersonate approval authority.
- [ ] Revocation, token rotation, audit access and rate limits are tested.

## Required adversarial case

A viewer writes a review by submitting another user’s name in a payload.

## Implementation surfaces

- `src/statement_ledger/auth.py`
- `src/statement_ledger/api.py`
- `tests/security/`

## Validation and completion evidence

Retain the exact command, environment, fixture or permitted source hash, result, and unresolved limitations. Mocked transport proves client behavior only; a source integration requires an authorized real fixture and bounded live proof. A model/throughput claim requires a real run. Add regression tests for both acceptance and refusal paths; regenerate affected schemas and specification before closing the ticket.

## Rollback

Keep the feature disabled until its gate passes. On regression, stop the new producer/consumer, preserve immutable record history and audit evidence, and restore the previously validated behavior. Do not erase conflicting evidence or reapprove stale descendants merely to recover green status.
