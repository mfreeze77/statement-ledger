---
id: SL-213
title: "Validate local speaker embeddings and target-speaker detection"
status: proposed
gate: G3
dependencies: ["SL-208", "SL-212"]
---

# SL-213: Validate local speaker embeddings and target-speaker detection

## Scope and contract

Upgrade work for the standalone Statement Ledger application. Implementation surfaces: `speech.py; evaluation/acoustics/`.
The status refers only to the named bounded scope; it does not close broader original source, production or real-model gates.

## Acceptance criteria

- [ ] Pin permitted model weights and dependencies; capture actual hardware and reference audio provenance.
- [ ] Measure cross-channel, overlap and short-turn behavior against verified labels.
- [ ] Keep acoustic scores advisory and enforce biometric processing grants.

## Required adversarial case

A voiceover or impersonation resembles the enrolled speaker acoustically or linguistically.

## Evidence and validation

Before closing, commit the exact executed command, environment/model revisions, authorized corpus hashes, measured results and refusal paths. Do not turn a mock or a synthetic fixture into a claimed real acceptance. Keep configuration disabled or shadow until this gate has evidence.

## Rollback

Disable the new producer or assist route, keep full-audio/manual review available, preserve revision history and raw failure receipts, and rebuild only approved derived indexes. Do not delete conflicting evidence or silently restore expired permissions.
