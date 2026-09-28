# PR #1 follow-up review corrections

Scope: review comment 5864414853 against 1b4dcbc. Same branch; additive plain
commits only, no rebase, force push, main write, merge, or repository-setting change.

## Item-to-test map

| Review item | Implementation | Regression evidence |
|---|---|---|
| 1: restore agent rule | Restore main's exact first-read sentence; keep the foundation section and add a separate foundation reading sentence. | `test_exact_main_read_instruction_restored` |
| 2: owner recovery | Local CLI can reparse and attach an intact retained receipt, or issue one audited retry permission keyed by request/provider. Reconciliation by itself grants no new spending. Legacy job-ID keyed operations use the same content lookup. | `test_reconciled_request_stays_blocked_without_owner_choice`, `test_owner_recovers_retained_receipt_then_worker_reuses_without_payment`, `test_authorized_new_attempt_can_succeed_after_reconciliation`, `test_owner_authorizes_one_new_attempt_not_unbounded_replay` |
| 2: concurrency and limits | Separate immutable attempts; one pending permission per content key; history snapshot, budget check, reservation and consumption share a transaction. Reasons/actors required. Explicit revocation supported. | `test_authorization_is_single_use_across_competing_connections`, `test_retry_authorization_fails_closed`, `test_unsent_cancel_consumes_one_authorized_reservation`, `test_authorization_revocation_is_explicit_and_audited`, `test_accounted_direct_call_cannot_hide_extra_transport_retries` |
| 2: evidence and interfaces | Receipt checksum, request metadata, status, source revisions/rights and response contract must match. SL-301 additionally requires an explicit capture-time operation binding, replacing capture-interval inference. Same transaction attaches the canonical advisory record and journal reference. No new HTTP mutation endpoint. | `test_receipt_recovery_rejects_invalid_or_inapplicable_evidence`, `test_receipt_recovery_revokes_unused_retry_permission`, `test_local_cli_owner_recovery_actions` |
| 3: cache parity | One shared eligibility function and lookup for direct/worker paths, including journal recovery. No alias reuse; no expired/future/naive timestamp reuse. An ineligible paid result blocks without owner authorization, rather than causing automatic re-spending. | `test_worker_never_reuses_alias_or_expired_canonical_or_journal_result`, `test_direct_path_uses_identical_cache_policy`, `test_pinned_current_direct_cache_preserves_identity`, `test_shared_cache_boundary`, `test_explicit_authorization_refreshes_instead_of_reusing_current_result` |
| Minor: deterministic heartbeat | Virtual queue clock plus hashing/renewal events replace 3.1/3.4-second sleeps. A competing connection checks after the original lease but before the renewed lease expires. Timeouts only detect deadlock; they do not determine lease correctness. | `test_heartbeat_covers_slow_artifact_hash_before_gpu_prepare` |

New tests are in `tests/test_followup_review.py`; the existing heartbeat test remains
in `tests/test_review_interfaces.py`. All providers and enrollment data are synthetic.

## Migration and compatibility

Migration **004** adds only the retry-permission table/index. Applied migrations
001–003 are unchanged. Opening a v3 database now requires explicit migration.
`test_migration_four_preserves_prior_operation_and_audit_rows` and
`test_fourth_migration_failure_preserves_v3_data` check upgrade and rollback. The
existing real v0.2 fixture tests still run; their expected migration inventory now
includes 004. The older reconstructed-schema fixture also removes the new empty table.
These inventory/fixture updates do not remove historical-preservation assertions.

`DecisionRun.latency_ms` now permits null for receipt recovery when original execution
latency was not retained. Recovery does not invent a zero or reset captured_at. Existing
numeric values remain valid and existing stored revisions/hashes are not rewritten.
The corresponding generated JSON schema is updated; canonical kind count stays 20.

## Owner operating procedure

Drain/stop the relevant worker before reconciling an uncertain external operation.
Cost reconciliation is not a provider cancellation and cannot retract an in-flight call.
Inspect local receipts and provider billing before resolving an ambiguous outcome.

1. Use existing `reconcile-operation` to document known cost when necessary.
2. Prefer `recover-operation-decision OPERATION_ID --receipt-id RECEIPT_ID --reason TEXT`.
   This performs zero network calls and retains original source/time provenance.
3. If a usable result cannot be recovered, use
   `authorize-operation-retry OPERATION_ID --reason TEXT`. This records the owner actor
   and reason and permits **one reservation**, without making a call or requeuing a job.
4. Explicitly requeue the failed/blocked job using `requeue-job JOB_ID --reason TEXT`.
   The worker still checks configuration, source rights, revisions, cancellation and budget.
5. An unused permission can be withdrawn with
   `revoke-operation-retry AUTHORIZATION_ID --reason TEXT`.

A reservation consumes permission even if cancelled before transmission; a known-unsent
attempt is recorded at zero external cost, but a consumed retry permission is never
silently restored. Budget refusal rolls back consumption. Changed operation history
requires explicit revocation/re-authorization. A fresh uncertain outcome requires another
reconciliation and a new explicit owner decision. Prior charges are never overwritten.
Recovered alias/expired results are historical records, not cache hits; they do not
relax the shared cache policy. No source, speaker, finding or model becomes live-verified.

## Review-sensitive surfaces and validation

Changes include AGENTS.md restoration, operation accounting/recovery, a new SQL migration,
a nullable telemetry field/schema, and the deterministic heartbeat regression. No CI
workflow, checker policy, allowlist, secret-scan configuration, credential transport,
rights rule, or result-commit fence is relaxed. No new secret is needed.

Run `python scripts/check.py check` in the locked environment; CI uses its unchanged
five jobs and requires `FOUNDATION_CHECK_COMPLETE` / `FOUNDATION_PROOF_COMPLETE`.
The completion comment and PR description record exact head, commands, actual Python
versions, counts and CI links. Earlier reports describe earlier revisions, not this head.

Not executed: live providers or paid requests, actual GPU inference, native Windows,
real-person media, and browser-driven UI. Local-owner actions are exposed only in the
existing local CLI; this review does not add remote operation-recovery authority.


## SL-301: immutable receipt-to-operation binding

The follow-up allowed a matching request and mutable capture interval to establish
ownership when `usage.receipt_ids` was absent. Re-reconciling operation A could enlarge
that interval enough to accept a receipt produced by its authorized retry B. SL-301
removes that inference entirely.

`OperationJournal.capture_receipt` now records the explicit originating operation ID
in a `provider.receipt_bound` audit entry **in the same transaction as the receipt
bytes and their original capture audit entry**. Both the worker and the accounted
direct Jev path use this method before response parsing/validation. A late callback
still supplies its original operation ID; capture never looks up the newest operation
for matching content. Failure to persist the binding rolls back the entire capture.

Ownership is separate from hashed request metadata, so semantic request hashes,
provider payloads, cache keys, and canonical validation remain unchanged. No schema
change or migration 005 is needed: the existing append-only audit stores this explicit
provenance fact. The audit lookup runs only during explicit owner recovery, not for
every model request. It requires exactly one matching binding; missing, conflicting,
malformed or duplicated bindings fail closed. Legacy receipts and unaccounted direct
captures without a recorded operation binding are retained but cannot be attached to
an operation. They are **not** backfilled from timestamps or matching content. The
existing explicit, single-use owner retry procedure remains available.

Recovery still checks request hash, body checksum, typed response, source rights and
staleness. It preserves `captured_at` and keeps `latency_ms` null. Timestamp sanity
(timezone-aware and not in the future) remains, but no operation time-window match is
used to establish or fall back to ownership.

`reconcile` now accepts only `started` and `unknown`. Completed, already-reconciled,
cancelled, and absent operations are refused without changing their rows or audit
history. Grant consumption must update exactly one row. A zero-row update raises and
rolls back the attempted reservation as well as all associated audit effects; the
existing budget calculation, grant basis, and worker commit fence are unchanged.

### Acceptance and hard-negative tests

All new tests are in `tests/test_receipt_binding.py` and use local SQLite, fictional
records and mocked transport only.

| Requirement | Regression |
|---|---|
| Capture belongs to its explicit operation before validation, including timeouts and malformed bodies | `test_capture_persists_operation_binding_before_response_validation` (worker/direct x three outcomes) |
| Exact A/reconcile/authorize/B/capture/reconcile-A sequence cannot misattribute B to A | `test_attempt_b_receipt_cannot_be_recovered_for_reconciled_attempt_a` (including further grant/revoke actions) |
| Matching request hash or usage receipt list cannot replace missing/mismatched ownership | `test_unbound_or_different_operation_receipt_is_refused` |
| Own receipt is recoverable with unchanged capture time and null latency, without an interval heuristic | `test_own_receipt_uses_binding_not_mutable_operation_time_window` |
| A second reconciliation is a no-op error | `test_reconcile_terminal_operation_is_refused_without_changes` |
| Started/unknown reconciliation remains functional | `test_reconcile_ambiguous_operation_still_succeeds` |
| Zero-row grant consumption creates no operation or audit changes | `test_zero_row_grant_consumption_rolls_back_reservation_and_audit` (real SQLite `RAISE(IGNORE)` trigger) |
| Receipt and binding commit atomically | `test_capture_and_binding_are_atomic` |
| A delayed A response cannot inherit active retry B's identity | `test_late_receipt_stays_bound_to_origin_not_current_retry` |
| Duplicate bindings and invalid capture ownership fail closed | `test_multiple_operation_bindings_are_refused`, `test_capture_refuses_mismatched_or_cancelled_operation` |

The earlier synthetic history helper now uses explicit bound capture. Its timestamp
negative tests a future timestamp, not the removed lower operation-window bound; the
new positive test covers that policy change. The changed-history grant test injects
an out-of-band history edit instead of invoking a now-prohibited second reconciliation.
Historical-preservation and permission assertions are retained.

### Scope clarification for the PR review

The ticket's file list omits `application/handlers.py`, but its worker callback owns the
actual operation ID. Its only change delegates that callback to
`journal.capture_receipt(operation_id, ...)`. Without this necessary capture-site
wiring the worker would continue producing unbound receipts. This small additional
file change is explicitly flagged for scope review; no worker lifecycle or commit-fence
code is changed. Applied SQL 001-004, cache rules, budget logic, agent rules, workflows,
secret-scanner settings and allowlists are untouched.

No live provider requests, paid calls, credentials, GPU inference or real-person data
are required. The PR completion comment supplies executed counts and CI evidence.
