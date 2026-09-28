---
id: SL-206
title: "Official TypeSafe transport and bounded model orchestration"
status: verified_mock_contract
gate: G2
dependencies: ["SL-205"]
---

# SL-206: Official TypeSafe transport and bounded model orchestration

## Scope and contract

Upgrade work for the standalone Statement Ledger application. Implementation surfaces: `jev.py; acceleration.py`.
The status refers only to the named bounded scope; it does not close broader original source, production or real-model gates.

## Acceptance criteria

- [x] Use only the official fixed TypeSafe endpoint with server-side credentials and pinned model.
- [x] Authorize every source dependency for provider submission before a call.
- [x] Validate exact typed question/answer identity, bound payloads/retries, and cache only current compatible decisions.

## Required adversarial case

A linked third-party provider endpoint, model alias drift or changed transcript attempts reuse.

## Evidence and validation

Read `docs/VALIDATION_REPORT.md`, the relevant tests under `tests/test_acceleration*.py` and `tests/test_jev.py`, and generated contracts. Local/synthetic tests do not establish real-world accuracy. Mocked contract statuses explicitly do not establish a successful live provider call.

## Rollback

Disable the new producer or assist route, keep full-audio/manual review available, preserve revision history and raw failure receipts, and rebuild only approved derived indexes. Do not delete conflicting evidence or silently restore expired permissions.
