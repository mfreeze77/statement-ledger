---
id: SL-207
title: "Raw capture and quantization-aware fault handling"
status: verified_mock_contract
gate: G2
dependencies: ["SL-206"]
---

# SL-207: Raw capture and quantization-aware fault handling

## Scope and contract

Upgrade work for the standalone Statement Ledger application. Implementation surfaces: `jev.py; store.py; tests/test_jev.py`.
The status refers only to the named bounded scope; it does not close broader original source, production or real-model gates.

## Acceptance criteria

- [x] Capture raw bytes and request metadata before JSON, status or semantic validation.
- [x] Preserve independently quantized values and compatibility warnings without silently renormalizing.
- [x] Retain unavailable status and errors; no fallback may manufacture a negative semantic answer.
- [x] Export exact receipt bytes with base64 and verify stored receipt hashes.

## Required adversarial case

An apparently valid probability vector has a separately quantized score; another response has duplicate JSON keys.

## Evidence and validation

Read `docs/VALIDATION_REPORT.md`, the relevant tests under `tests/test_acceleration*.py` and `tests/test_jev.py`, and generated contracts. Local/synthetic tests do not establish real-world accuracy. Mocked contract statuses explicitly do not establish a successful live provider call.

## Rollback

Disable the new producer or assist route, keep full-audio/manual review available, preserve revision history and raw failure receipts, and rebuild only approved derived indexes. Do not delete conflicting evidence or silently restore expired permissions.
