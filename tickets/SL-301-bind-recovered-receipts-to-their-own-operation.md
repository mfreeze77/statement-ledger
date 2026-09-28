---
id: SL-301
title: "Bind recovered receipts to their own provider operation"
status: ready_for_codex
gate: G2
pillar: platform
dependencies: ["SL-207"]
---

# SL-301: Bind recovered receipts to their own provider operation

## Goal

A retained provider receipt can be attached only to the provider operation that produced
it. Today, when an operation has no `receipt_ids` (the timed-out case), receipt recovery
falls back to matching by time window, and `reconcile()` accepts an operation that is
already `completed` and resets its `finished_at`. Failure sequence: operation A times out
and is reconciled; the owner authorizes one retry, attempt B captures receipt R_B; the
owner reconciles A again, widening A's window; R_B can then be recovered as A's decision.
No money is spent, but provenance is misattributed.

## Scope: files and modules that may change

- `src/statement_ledger/application/operation_recovery.py`
- `src/statement_ledger/infrastructure/operations.py`
- `src/statement_ledger/infrastructure/providers/jev.py` (only the receipt-capture call site, if needed to record the operation id)
- `tests/test_followup_review.py` or a new `tests/test_receipt_binding.py`
- `docs/PR1_FOLLOWUP_FIXES.md` (note the change)

## Out of scope

Changing applied migrations 001-004, the commit fence, cache rules, budget logic, CI
workflows or the secret-scan configuration. If a schema change is unavoidable, add a new
migration 005 and call it out in the PR description.

## Inputs and outputs (record kinds and contracts)

- Each captured provider receipt records the id of the operation it belongs to.
- Recovery accepts a receipt only when that recorded operation id equals the operation
  being recovered, in addition to the existing request-hash, body-hash, validator, rights
  and staleness checks. The time-window match is removed, not kept as a fallback.
- `reconcile()` refuses an operation that is not in an ambiguous state (`started` or
  `unknown`); reconciling a `completed` operation is an error and changes nothing.
- The single-use grant consumption checks that its `UPDATE` changed exactly one row and
  raises otherwise.

## Acceptance tests (must pass in CI without secrets)

- Receipt captured by attempt B cannot be recovered for operation A, including after any
  sequence of owner reconcile and authorize actions.
- A receipt with no recorded operation id is refused for recovery.
- Recovery of an operation's own receipt still succeeds, keeps the original `captured_at`
  and leaves `latency_ms` null.
- Reconciling a `completed` operation raises and leaves `state`, `finished_at` and audit
  history unchanged.
- Grant consumption that affects zero rows raises and begins no operation.

## Hard negatives (inputs that must be rejected)

- The exact A/B sequence above.
- A receipt whose request hash matches but whose operation id differs.
- A second `reconcile()` of the same operation.

## Live checks for Claude

None.

## Secrets needed

None.
