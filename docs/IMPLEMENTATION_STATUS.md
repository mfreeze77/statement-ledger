# Implementation status — v0.3.0

See [Phase 0 status](PHASE0_STATUS.md), [operating guide](runbooks/FOUNDATION.md) and [validation](PHASE0_VALIDATION.md). Historical product chapters do not supersede this table. Root Python modules are temporary compatibility exports to the new module owners.

| ID | Capability | State | Evidence | Boundary |
|---|---|---|---|---|
| SL-C01 | Single-owner local application | implemented_local_tested | api.py; store.py; cli.py | Authenticated API and inspector; not multi-user SaaS. |
| SL-C02 | Typed canonical records | implemented_local_tested | models.py; acceleration_models.py; contracts/ | 20 record kinds; schemas generated from actual implementation. |
| SL-C03 | Versioning and optimistic concurrency | implemented_local_tested | store.py; test_domain.py | Append-only revisions; expected_revision required for updates. |
| SL-C04 | Dependency invalidation | implemented_local_tested | service.py; store.py | Parent revisions make descendants stale; no silent reapproval. |
| SL-C05 | Person source planner | implemented_local_tested | discovery.py; sources.json | All 47 entries retained; primary-evidence sources are claim-driven, not name-queried; does not automatically execute them. |
| SL-C06 | File ingestion and parsers | implemented_local_tested | connectors/parsers.py; ingest.py | Synthetic format fixtures; no large live-corpus bakeoff. |
| SL-C07 | Four public API client surfaces | implemented_mock_tested | connectors/http.py; test_http.py | YouTube metadata, Google fact-check, Archive, AAPB metadata. Real response proof pending. |
| SL-C08 | Other named source integrations | specified_access_dependent | sources.json; docs/sources/ | Registry contracts and manual input path; no invented vendor endpoints. |
| SL-C09 | VTT/SRT and ASR export imports | implemented_local_tested | transcripts.py | Local labels and segment timing; not verified real-world speaker identity. |
| SL-C10 | Optional speech inference | implemented_not_live_executed | speech.py; media_work.py | faster-whisper, pyannote and local SpeechBrain adapter logic; no real weights or inference benchmark. |
| SL-C11 | Reviewed speaker mapping | implemented_local_tested | service.py; speech.py | Human-reviewed identity mappings; optional advisory acoustic comparison exists but is not live-validated. |
| SL-C12 | Local audio/video clip invocation | implemented_local_tested | media.py; test_media.py | FFmpeg synthetic WAV execution passed; video-format matrix pending. |
| SL-C13 | Exact reviewed event-coordinate deduplication | implemented_local_tested | service.py; test_domain.py | Copy and original collapse at identical verified boundaries. Fuzzy/piecewise matching pending. |
| SL-C14 | Claim/evidence/review recording | implemented_local_tested | models.py; service.py | Validation of provenance/scope/relations; humans supply interpretations. Not autonomous fact-checking. |
| SL-C15 | Corrections | partly_implemented | models.py; service.py; claim_library.py | Open corrections block review-card reuse; explicit resolved records supported; full adjudication UI pending. |
| SL-C16 | Coverage records | partly_implemented | models.py; service.py | Manual bounded coverage records; automatic run reconciliation pending. |
| SL-C17 | Durable job leases | implemented_local_tested | infrastructure/queue.py; infrastructure/worker.py; application/handlers.py | Connected same-DB worker/outbox, leases, heartbeats, cancellation and fenced results. Explicit handlers only; no autonomous scheduler. |
| SL-C18 | Raw retention and rights | partly_implemented | ingest.py; policy.py | Source-level grants and expiry gates; purge/revocation propagation and asset-level grants pending. |
| SL-C19 | Operator UI | implemented_static_route_tested_browser_blocked | static/; tests/test_acceleration_interfaces.py | Profiles, window planner and claim-search views added; actual browser navigation blocked, no visual pass. |
| SL-C20 | Auditing and backup | implemented_local_tested | store.py; cli.py | Native SQLite backup, exact-byte provider receipt retention and JSON base64 export; not externally witnessed tamper-proof storage. |
| SL-C21 | Production database and deployment | partly_implemented | Dockerfile; compose.yaml; infrastructure/migrations/; docs/runbooks/FOUNDATION.md | Single-owner local SQLite environments/migrations delivered. Multi-user SaaS, PostgreSQL and production rollout are not implemented. |
| SL-C22 | Real subject investigation | not_executed | config/subject.scott-jennings.json | Name-only seed. No real appearances, quotes, allegations, or findings loaded. |
| SL-C23 | Remote GitHub repository | created_and_baseline_ci_verified | mfreeze77/statement-ledger main ffcb18b; GitHub Actions baseline run 36360621237 | Phase 0 edits are proposed in a branch/PR; original main history is preserved. |
| SL-C24 | Public publication | disabled_and_not_implemented | docs/spec/16_EVALUATION_AND_RELEASE_GATES.md | Internal research only; independent publication, permissions and review gates required. |
| SL-C25 | Shared claim library and seed ingestion | implemented_local_tested | claim_library.py; claim_seeds.py | FTS5 and exact seed dedup; no automatic truth import or large real-corpus benchmark. |
| SL-C26 | Reusable reviewed evidence cards | implemented_local_tested | claim_library.py; acceleration_service.py | Current exact proposition/review bindings, expiry, corrections and scope; never automatic verdict reuse. |
| SL-C27 | Event-deduplicated language profiles | implemented_local_tested | profiles.py | Accepted target/background turns only; opening/closing/interior n-grams; no learned rhetorical classifier. |
| SL-C28 | Incremental accepted-turn refresh | implemented_local_tested | profiles.py; cli.py; api.py | Explicit refresh, holdout exclusions and curated comparison people; no always-on subscriber. |
| SL-C29 | Caption-first window localization | implemented_local_tested | localization.py; intervals.py | Shadow/assist windows with gaps, audits, unions and full fallback; research thresholds are uncalibrated. |
| SL-C30 | TypeSafe Jev transport and cache | implemented_mock_tested | jev.py; tests/test_jev.py | Official endpoint and raw capture; retries, typed validation and quantization diagnostics; no live provider proof. |
| SL-C31 | Jev claim and window orchestration | implemented_mock_tested | acceleration.py; claim_library.py | Bounded batches and cached typed proposals; no identity or finding approval. |
| SL-C32 | Selective local audio execution | implemented_local_tested | media_work.py; media.py | Synthetic FFmpeg execution and durable manifests verified; real ASR/diarization unexecuted. |
| SL-C33 | Localization evaluation and cost estimates | implemented_local_tested | evaluation.py | Coverage/calibration diagnostics and user-priced costs; no fitted calibrator, deployed thresholds or real speedup guarantee. |
| SL-C34 | Additive v0.1 database upgrade | implemented_local_tested | infrastructure/migrations/; tests/test_foundation.py | Numbered checksummed legacy adoption; no historical payload/hash rewrite; native backup and explicit runtime migration required. |

Next evidence gate: authorized held-out recordings, reviewed attribution labels, and explicit GPU/provider prerequisites. Keep default shadow mode until real measurements justify a policy change.
