# PR #1 review remediation

Review: issue comment 5863821339, against head `1676b0e`.
Scope: the twelve requested corrections, their regressions, and integration of main `0ec7b74`.
No product/source expansion, paid calls, live providers, GPU inference, or real-person data.

## Integration and protected rules

Main's Codex rules, CLAUDE.md, AGENT_WORKFLOW.md and exact-marker live-test gate are retained.
The main integration is an additive merge on the same PR branch, not a force-pushed rebase:
main's explicit no-rewrite rule takes precedence over using a particular integration command.
Neither main nor repository settings are changed by this remediation.

The existing Phase 0 workflow and secret-scan exceptions are unchanged in these fixes.
The pytest live marker/hook from main is preserved; `SL_RUN_LIVE` is documented as a control
variable and accepted by settings without enabling live tests or paid work automatically.
The new authenticated requeue endpoint adds generated OpenAPI and runtime-schema output.
Frozen v0.2 source is stored as plaintext .py.txt test input; it is not an encoded payload,
executable delivery mechanism, or a workflow that writes code into the repository.
The original Phase 0 CI/allowlist changes still require the owner's review before merge.

## Item-to-test map

All tests below run offline, using fictional records, mock transport, or generated audio.
Paths are under tests/; parameterized cases count as separate pytest tests.

| Review item | Implementation | Regression tests |
|---|---|---|
| 1. Paid cancellation | Check ownership before reservation and immediately before transport; unsent reservations record known zero cost. | test_review_jobs.py: test_cancelled_after_claim_never_reserves_or_calls; test_cancel_immediately_before_reservation_never_spends; test_cancel_after_reservation_before_network_is_known_zero |
| 2. Duplicate payment | Content-keyed operations and recoverable completed proposals; top-level input sets canonicalized; run ID/retry policy excluded from job identity. | test_review_jobs.py: test_retry_policy_and_input_order_do_not_duplicate_payment; test_cross_job_content_cache_is_shared; test_content_reservation_is_atomic_across_operation_ids; test_positional_provider_bindings_not_reordered_by_job_identity |
| 3. Recovery | Classify non-paid transport/timeout and SQLite contention as transient; preserve ambiguous paid reservations; audited bounded requeue and explicit terminal submission reports. | test_review_jobs.py: test_non_paid_transient_work_retries_with_audit; test_completed_remote_proposal_recovers_after_busy_commit; test_ambiguous_paid_call_never_auto_retries_even_after_requeue; test_requeue_preserves_attempt_history_and_does_not_retry_validation; test_blocked_job_recovers_only_after_explicit_requeue; test_review_interfaces.py: test_actual_source_client_exhaustion_is_classified_retryable; test_source_rejection_is_not_transient; test_submit_terminal_report_and_requeue_api_and_cli |
| 4. Actual legacy adoption and WAL | Load checksum-verified Store/JobQueue/util source from ffcb18b, not today's SQL; use WAL, FTS, v2 migration row, in-ledger jobs and populated history. Snapshot copies are self-contained DELETE-journal databases. | test_review_storage.py: test_real_v02_wal_fts_jobs_and_exact_historical_rows_survive; test_real_v02_pending_in_ledger_job_blocks_without_changes; test_backup_restore_actual_wal_snapshot_in_isolated_fixture |
| 5. Core schema | Require all core as well as runtime tables before opening or restoring. | test_review_storage.py: test_missing_all_core_tables_refused_at_open_and_restore |
| 6. Windows artifact keys | Normalize relative orphan keys with as_posix(). | test_review_storage.py: test_windows_orphan_keys_are_posix_not_backslashes |
| 7. Main integration | Preserve rules and marker hook; register/document SL_RUN_LIVE; retain the two ordinary tests whose parameter name is live. | test_review_interfaces.py: test_live_control_environment_is_registered_and_offline_startup_safe; test_live_marker.py (two ordinary cases pass; actual live case skipped) |
| 8. Authentication | Compare UTF-8 bytes so a malformed/non-ASCII header cannot raise compare_digest TypeError. | test_review_interfaces.py: test_non_ascii_authorization_is_401_not_500 |
| 9. Google credentials | X-goog-api-key request header, never key query parameters; transport errors retain retry classification. | test_review_interfaces.py: test_google_credentials_only_in_headers_never_urls_or_info_logs |
| 10. Backup/restore | Clean owned destination after initialization failures; verify the actual copied database before opening it. | test_review_storage.py: test_failed_backup_initialization_cleans_destination_and_can_retry; test_failed_artifact_initialization_cleans_backup; test_restore_detects_corruption_in_copied_database |
| 11. Finished legacy work | Retain terminal rows unchanged; reject only non-terminal or unknown job schemas. | test_review_storage.py: test_finished_separate_legacy_jobs_preserved_not_blocking; in-ledger success/failed cases in item 4 |
| 12. Hashing lease race | Start heartbeat before input/artifact verification; recheck ownership before prepare. | test_review_interfaces.py: test_heartbeat_covers_slow_artifact_hash_before_gpu_prepare |

## Recovery semantics

`enqueue` / POST /api/jobs returns job_id, actual state, reused and requeue_required.
A repeated submission never silently revives failed, blocked or cancelled work. The legacy
Python submit() returns the ID for non-recovery states and raises JobRequiresRequeue for
terminal failures/cancellation. Existing job IDs and pending outbox identities remain usable.

Use `requeue-job ID --reason "reviewed recovery reason" --additional-attempts 1` or the
authenticated POST /api/jobs/{id}/requeue body with those two fields. Attempt ordinals and
previous receipts are never reset. Rights, exact input revisions, cancellation, configuration
and publication fencing still apply to every attempt. Unknown paid outcomes remain blocked:
requeue and cost reconciliation alone are NOT authorization to repeat a paid request.
A retained successful proposal can complete after database contention without another call.
Cancellation before transport is known-unsent; cancellation during an in-flight provider call
cannot retract that external effect and still prevents canonical result publication.

Provider bindings and input_ids inside the semantic request remain ordered. Only the outer
job's dependency set is order-insensitive. Reordering semantic query/candidate roles would
change the meaning of claim matching and is explicitly tested as a hard negative.

## Executed evidence and limits

Baseline on the reviewed head: 299 passed. Current remediation: 341 passed, 1 live skipped
locally before publication. Final head CI counts, real interpreter versions and completion
markers are recorded in the PR description after the run, rather than assumed here.
No baseline tests/assertions were removed to obtain a pass; the original approximate legacy
fixture remains in addition to the new frozen-code fixture.

The Windows key regression simulates Windows separators with PureWindowsPath on Linux;
this is not a native Windows test run. The slow-hash race uses a fake GPU-capability handler,
real SQLite connections and a real heartbeat; no GPU inference is claimed.
The WAL backup test genuinely reads a WAL source and restores a real SQLite snapshot. In
that isolated single-process fixture only, the runtime WAL-version approval is mocked because
the sandbox's linked SQLite is older than the production gate. This does not approve that
runtime for concurrent production WAL; the production gate and its tests are unchanged.
No real credentials, provider calls, datasets or model weights are needed for this test set.
