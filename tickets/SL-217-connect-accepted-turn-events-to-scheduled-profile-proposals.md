---
id: SL-217
title: "Connect accepted-turn events to scheduled profile proposals"
status: proposed
gate: G3
dependencies: ["SL-204", "SL-017"]
---

# SL-217: Connect accepted-turn events to scheduled profile proposals

## Scope and contract

Upgrade work for the standalone Statement Ledger application. Implementation surfaces: `jobs.py; outbox worker; profile proposal service`.
The status refers only to the named bounded scope; it does not close broader original source, production or real-model gates.

## Acceptance criteria

- [ ] Idempotently subscribe to accepted/revised turns and propose new profile revisions.
- [ ] Keep reviewer-controlled background selection and holdout partitions.
- [ ] Never automatically promote a profile without its event-held-out evaluation gate.

## Required adversarial case

Replayed outbox messages multiply profile support or create an unbounded refresh loop.

## Evidence and validation

Before closing, commit the exact executed command, environment/model revisions, authorized corpus hashes, measured results and refusal paths. Do not turn a mock or a synthetic fixture into a claimed real acceptance. Keep configuration disabled or shadow until this gate has evidence.

## Rollback

Disable the new producer or assist route, keep full-audio/manual review available, preserve revision history and raw failure receipts, and rebuild only approved derived indexes. Do not delete conflicting evidence or silently restore expired permissions.
