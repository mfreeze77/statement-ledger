---
id: SL-208
title: "Selective media execution and offset-preserving manifests"
status: verified_synthetic_media
gate: G3
dependencies: ["SL-205"]
---

# SL-208: Selective media execution and offset-preserving manifests

## Scope and contract

Upgrade work for the standalone Statement Ledger application. Implementation surfaces: `media_work.py; media.py; speech.py`.
The status refers only to the named bounded scope; it does not close broader original source, production or real-model gates.

## Acceptance criteria

- [x] Input SHA, path root, source rights and current plan must pass before work.
- [x] Each clip preserves source start/end plus local ASR times and namespaced diarization labels.
- [x] Write execution manifest before processing and on failure; never auto-confirm an identity.

## Required adversarial case

Two clips both return speaker_0, or FFmpeg fails after one clip has completed.

## Evidence and validation

Read `docs/VALIDATION_REPORT.md`, the relevant tests under `tests/test_acceleration*.py` and `tests/test_jev.py`, and generated contracts. Local/synthetic tests do not establish real-world accuracy. Mocked contract statuses explicitly do not establish a successful live provider call.

## Rollback

Disable the new producer or assist route, keep full-audio/manual review available, preserve revision history and raw failure receipts, and rebuild only approved derived indexes. Do not delete conflicting evidence or silently restore expired permissions.
