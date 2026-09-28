---
id: SL-212
title: "Build independently labeled cross-program localization corpus"
status: proposed
gate: G3
dependencies: ["SL-203", "SL-205"]
---

# SL-212: Build independently labeled cross-program localization corpus

## Scope and contract

Upgrade work for the standalone Statement Ledger application. Implementation surfaces: `evaluation/localization/; docs/runbooks/`.
The status refers only to the named bounded scope; it does not close broader original source, production or real-model gates.

## Acceptance criteria

- [ ] Use authorized full events, verified speakers, event/topic/date splits and similar comparison speakers.
- [ ] Preserve short turns, overlap, quotations, poor captions and uncertain labels.
- [ ] Compare phrase-only, Jev-assisted and audio-first coverage and actual total work on identical splits.

## Required adversarial case

Train and test accidentally contain different uploads of the same event.

## Evidence and validation

Before closing, commit the exact executed command, environment/model revisions, authorized corpus hashes, measured results and refusal paths. Do not turn a mock or a synthetic fixture into a claimed real acceptance. Keep configuration disabled or shadow until this gate has evidence.

## Rollback

Disable the new producer or assist route, keep full-audio/manual review available, preserve revision history and raw failure receipts, and rebuild only approved derived indexes. Do not delete conflicting evidence or silently restore expired permissions.
