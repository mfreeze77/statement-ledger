---
id: SL-220
title: "Purge revoked source-derived profiles and provider artifacts"
status: proposed
gate: G2
dependencies: ["SL-006", "SL-207"]
---

# SL-220: Purge revoked source-derived profiles and provider artifacts

## Scope and contract

Upgrade work for the standalone Statement Ledger application. Implementation surfaces: `retention worker; store.py; authorization`.
The status refers only to the named bounded scope; it does not close broader original source, production or real-model gates.

## Acceptance criteria

- [ ] Propagate rights revocation through derived profiles, cached decisions, raw state and exports.
- [ ] Test deletion/retention conflicts while preserving required minimal audit without source content.
- [ ] Exercise backup restoration under changed rights and prevent resurrected prohibited content.

## Required adversarial case

A rights-expired recording remains embedded in a cached provider request state.

## Evidence and validation

Before closing, commit the exact executed command, environment/model revisions, authorized corpus hashes, measured results and refusal paths. Do not turn a mock or a synthetic fixture into a claimed real acceptance. Keep configuration disabled or shadow until this gate has evidence.

## Rollback

Disable the new producer or assist route, keep full-audio/manual review available, preserve revision history and raw failure receipts, and rebuild only approved derived indexes. Do not delete conflicting evidence or silently restore expired permissions.
