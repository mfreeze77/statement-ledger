---
id: SL-215
title: "Benchmark broad paraphrase retrieval and large claim storage"
status: proposed
gate: G3
dependencies: ["SL-201", "SL-202"]
---

# SL-215: Benchmark broad paraphrase retrieval and large claim storage

## Scope and contract

Upgrade work for the standalone Statement Ledger application. Implementation surfaces: `claim_library.py; storage adapters; evaluation/retrieval/`.
The status refers only to the named bounded scope; it does not close broader original source, production or real-model gates.

## Acceptance criteria

- [ ] Use licensed real claim corpora and separate exact retrieval from semantic candidate generation.
- [ ] Measure memory, ingest throughput, search percentiles, card expansion and stale-index recovery.
- [ ] Consider PostgreSQL or hybrid retrieval only after evidence; never auto-merge by similarity.

## Required adversarial case

Similar phrasing differs only in year, denominator, negation or accounting basis.

## Evidence and validation

Before closing, commit the exact executed command, environment/model revisions, authorized corpus hashes, measured results and refusal paths. Do not turn a mock or a synthetic fixture into a claimed real acceptance. Keep configuration disabled or shadow until this gate has evidence.

## Rollback

Disable the new producer or assist route, keep full-audio/manual review available, preserve revision history and raw failure receipts, and rebuild only approved derived indexes. Do not delete conflicting evidence or silently restore expired permissions.
