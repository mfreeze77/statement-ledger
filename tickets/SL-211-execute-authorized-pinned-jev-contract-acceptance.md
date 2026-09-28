---
id: SL-211
title: "Execute authorized pinned Jev contract acceptance"
status: proposed
gate: G2
dependencies: ["SL-206", "SL-207"]
---

# SL-211: Execute authorized pinned Jev contract acceptance

## Scope and contract

Upgrade work for the standalone Statement Ledger application. Implementation surfaces: `evaluation/provider-acceptance/; docs/runbooks/`.
The status refers only to the named bounded scope; it does not close broader original source, production or real-model gates.

## Acceptance criteria

- [ ] Capture bounded real requests/responses with permission, key redaction and pinned version.
- [ ] Confirm request/response fields, rate limits, quantization regimes and billed usage against actual service.
- [ ] Compare repeated requests and error conditions without weakening typed validation.

## Required adversarial case

A model version changes field precision or returns a genuine structurally new answer.

## Evidence and validation

Before closing, commit the exact executed command, environment/model revisions, authorized corpus hashes, measured results and refusal paths. Do not turn a mock or a synthetic fixture into a claimed real acceptance. Keep configuration disabled or shadow until this gate has evidence.

## Rollback

Disable the new producer or assist route, keep full-audio/manual review available, preserve revision history and raw failure receipts, and rebuild only approved derived indexes. Do not delete conflicting evidence or silently restore expired permissions.
