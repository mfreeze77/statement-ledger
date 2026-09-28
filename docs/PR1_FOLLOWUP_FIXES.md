# PR #1 follow-up review corrections

Scope: review comment 5864414853 against 1b4dcbc. Same branch; additive plain
commits only, no rebase, force push, main write, merge, or repository-setting change.

## Item-to-test map

| Review item | Implementation | Regression evidence |
|---|---|---|
| 1: restore agent rule | Restore main's exact first-read sentence; keep the foundation section and add a separate foundation reading sentence. | `test_exact_main_read_instruction_restored` |
| 2: owner recovery | Local CLI can reparse and attach an intact retained receipt, or issue one audited retry permission keyed by request/provider. Reconciliation by itself grants no new spending. Legacy job-ID keyed operations use the same content lookup. | `test_reconciled_request_stays_blocked_without_owner_choice`, `test_owner_recovers_retained_receipt_then_worker_reuses_without_payment`, `test_authorized_new_attempt_can_succeed_after_reconciliation`, `test_owner_authorizes_one_new_attempt_not_unbounded_replay` |
| 2: concurrency and limits | Separate immutable attempts; one pending permission per content key; history snapshot, budget check, reservation and consumption share a transaction. Reasons/actors required. Explicit revocation supported. | `test_authorization_is_single_use_across_competing_connections`, `test_retry_authorization_fails_closed`, `test_unsent_cancel_consumes_one_authorized_reservation`, `test_authorization_revocation_is_explicit_and_audited`, `test_accounted_direct_call_cannot_hide_extra_transport_retries` |
| 2: evidence and interfaces | Receipt checksum, request metadata, status, capture interval, source revisions/rights and response contract must match. Same transaction attaches the canonical advisory record and journal reference. No new HTTP mutation endpoint. | `test_receipt_recovery_rejects_invalid_or_inapplicable_evidence`, `test_receipt_recovery_revokes_unused_retry_permission`, `test_local_cli_owner_recovery_actions` |
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
