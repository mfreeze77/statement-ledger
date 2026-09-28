---
id: SL-219
title: "Measure and route by all-in processing cost"
status: proposed
gate: G3
dependencies: ["SL-209", "SL-211", "SL-213"]
---

# SL-219: Measure and route by all-in processing cost

## Scope and contract

Upgrade work for the standalone Statement Ledger application. Implementation surfaces: `cost ledger; router; evaluation/performance/`.
The status refers only to the named bounded scope; it does not close broader original source, production or real-model gates.

## Acceptance criteria

- [ ] Measure acquisition, token input/output, failed calls, clip overhead, verification and full-audio baseline.
- [ ] Reuse shared source-asset derivations across people and select a full-audio route when cheaper.
- [ ] Keep measured usage and estimated prices separate with model/config revision.

## Required adversarial case

Five targets cover nearly all audio and separate screening duplicates the processing cost.

## Evidence and validation

Before closing, commit the exact executed command, environment/model revisions, authorized corpus hashes, measured results and refusal paths. Do not turn a mock or a synthetic fixture into a claimed real acceptance. Keep configuration disabled or shadow until this gate has evidence.

## Rollback

Disable the new producer or assist route, keep full-audio/manual review available, preserve revision history and raw failure receipts, and rebuild only approved derived indexes. Do not delete conflicting evidence or silently restore expired permissions.
