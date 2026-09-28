# Ticket index

85 bounded work packages. Original IDs and source onboarding tickets are retained. SL-201–SL-220 cover the v0.2 acceleration release and remaining acceptance work.

| Ticket | Title | Status | Gate | Dependencies |
|---|---|---|---|---|
| [SL-001](SL-001-establish-the-independent-local-reference.md) | Establish the independent local reference | verified_local_reference | G1 | — |
| [SL-002](SL-002-resolve-a-reproducible-dependency-and-model-environment.md) | Resolve a reproducible dependency and model environment | proposed | G1 | SL-001 |
| [SL-003](SL-003-unify-discovery-receipts-with-provenance-and-coverage.md) | Unify discovery receipts with provenance and coverage | proposed | G2 | SL-001 |
| [SL-004](SL-004-capture-real-connector-contracts-and-drift-quarantine.md) | Capture real connector contracts and drift quarantine | proposed | G2 | SL-003 |
| [SL-005](SL-005-constrain-media-acquisition-and-external-model-egress.md) | Constrain media acquisition and external-model egress | proposed | G2 | SL-003 |
| [SL-006](SL-006-add-asset-scoped-rights-and-retention-inheritance.md) | Add asset-scoped rights and retention inheritance | proposed | G2 | SL-003 |
| [SL-007](SL-007-support-bounded-large-json-arrays-and-resumable-corpora.md) | Support bounded large JSON arrays and resumable corpora | proposed | G2 | SL-004 |
| [SL-008](SL-008-resolve-original-events-and-near-duplicate-assets.md) | Resolve original events and near-duplicate assets | proposed | G4 | SL-004 |
| [SL-009](SL-009-implement-piecewise-timeline-alignment-and-occurrence-clusters.md) | Implement piecewise timeline alignment and occurrence clusters | proposed | G4 | SL-008 |
| [SL-010](SL-010-execute-and-benchmark-the-speech-worker.md) | Execute and benchmark the speech worker | proposed | G3 | SL-002, SL-005 |
| [SL-011](SL-011-calibrate-speaker-identity-proposals.md) | Calibrate speaker identity proposals | proposed | G3 | SL-010 |
| [SL-012](SL-012-build-the-transcript-and-context-review-workspace.md) | Build the transcript and context review workspace | proposed | G3 | SL-010, SL-011 |
| [SL-013](SL-013-add-constrained-candidate-claim-extraction.md) | Add constrained candidate claim extraction | proposed | G5 | SL-012 |
| [SL-014](SL-014-retrieve-primary-evidence-with-reproducible-snapshots.md) | Retrieve primary evidence with reproducible snapshots | proposed | G5 | SL-005, SL-013 |
| [SL-015](SL-015-extend-scope-compatibility-and-review-controls.md) | Extend scope compatibility and review controls | proposed | G5 | SL-014 |
| [SL-016](SL-016-implement-correction-resolution-and-re-review-tasks.md) | Implement correction resolution and re-review tasks | proposed | G5 | SL-015 |
| [SL-017](SL-017-version-ledger-snapshots-and-counting-policies.md) | Version ledger snapshots and counting policies | proposed | G4 | SL-009, SL-016 |
| [SL-018](SL-018-reconcile-discovery-coverage-and-source-gaps.md) | Reconcile discovery coverage and source gaps | proposed | G3 | SL-003, SL-004 |
| [SL-019](SL-019-connect-transactional-outbox-and-bounded-workers.md) | Connect transactional outbox and bounded workers | proposed | G6 | SL-003, SL-010 |
| [SL-020](SL-020-enforce-collection-and-model-budgets.md) | Enforce collection and model budgets | proposed | G6 | SL-019 |
| [SL-021](SL-021-migrate-canonical-storage-for-multi-worker-operation.md) | Migrate canonical storage for multi-worker operation | proposed | G6 | SL-017, SL-019 |
| [SL-022](SL-022-add-content-addressed-object-storage-and-manifests.md) | Add content-addressed object storage and manifests | proposed | G6 | SL-006, SL-019 |
| [SL-023](SL-023-introduce-production-identities-and-authorization.md) | Introduce production identities and authorization | proposed | G6 | SL-021 |
| [SL-024](SL-024-provide-opt-in-change-notifications.md) | Provide opt-in change notifications | proposed | G6 | SL-017, SL-019, SL-023 |
| [SL-025](SL-025-gate-private-exports-and-any-future-publication.md) | Gate private exports and any future publication | blocked | G7 | SL-016, SL-017, SL-023, SL-026 |
| [SL-026](SL-026-propagate-expiry,-deletion-and-redaction.md) | Propagate expiry, deletion and redaction | proposed | G6 | SL-006, SL-022 |
| [SL-027](SL-027-build-a-held-out-real-media-evaluation-corpus.md) | Build a held-out real-media evaluation corpus | proposed | G3 | SL-010, SL-011, SL-018 |
| [SL-028](SL-028-measure-workload-limits-and-recovery-behavior.md) | Measure workload limits and recovery behavior | proposed | G6 | SL-019, SL-021, SL-022 |
| [SL-029](SL-029-add-operational-observability-without-source-leakage.md) | Add operational observability without source leakage | proposed | G6 | SL-019 |
| [SL-030](SL-030-harden-packaging-and-release-reproducibility.md) | Harden packaging and release reproducibility | proposed | G6 | SL-002, SL-028 |
| [SL-031](SL-031-complete-the-first-private-person-centered-investigation.md) | Complete the first private person-centered investigation | proposed | G3 | SL-003, SL-004, SL-006, SL-010, SL-011, SL-018, SL-027 |
| [SL-101](SL-101-source-youtube.md) | Onboard YouTube Data API | access_and_contract_gate | G2 | SL-003, SL-004, SL-006 |
| [SL-102](SL-102-source-cnn_transcripts.md) | Onboard CNN program transcripts | access_and_contract_gate | G2 | SL-003, SL-004, SL-006 |
| [SL-103](SL-103-source-cbs_transcripts.md) | Onboard CBS program transcripts | access_and_contract_gate | G2 | SL-003, SL-004, SL-006 |
| [SL-104](SL-104-source-internet_archive.md) | Onboard Internet Archive | access_and_contract_gate | G2 | SL-003, SL-004, SL-006 |
| [SL-105](SL-105-source-gdelt_tv.md) | Onboard GDELT Television Explorer | access_and_contract_gate | G2 | SL-003, SL-004, SL-006 |
| [SL-106](SL-106-source-gdelt_visual.md) | Onboard GDELT Visual Explorer | access_and_contract_gate | G2 | SL-003, SL-004, SL-006 |
| [SL-107](SL-107-source-gdelt_tv_ngrams.md) | Onboard GDELT Television Ngrams | access_and_contract_gate | G2 | SL-003, SL-004, SL-006 |
| [SL-108](SL-108-source-gdelt_gqg.md) | Onboard GDELT Global Quotation Graph | access_and_contract_gate | G2 | SL-003, SL-004, SL-006 |
| [SL-109](SL-109-source-quotebank.md) | Onboard Quotebank | access_and_contract_gate | G2 | SL-003, SL-004, SL-006 |
| [SL-110](SL-110-source-media_cloud.md) | Onboard Media Cloud | access_and_contract_gate | G2 | SL-003, SL-004, SL-006 |
| [SL-111](SL-111-source-lexisnexis.md) | Onboard LexisNexis / Nexis Uni | access_and_contract_gate | G2 | SL-003, SL-004, SL-006 |
| [SL-112](SL-112-source-tveyes.md) | Onboard TVEyes | access_and_contract_gate | G2 | SL-003, SL-004, SL-006 |
| [SL-113](SL-113-source-critical_mention.md) | Onboard Critical Mention | access_and_contract_gate | G2 | SL-003, SL-004, SL-006 |
| [SL-114](SL-114-source-sprinklr.md) | Onboard Sprinklr | access_and_contract_gate | G2 | SL-003, SL-004, SL-006 |
| [SL-115](SL-115-source-snapstream.md) | Onboard SnapStream | access_and_contract_gate | G2 | SL-003, SL-004, SL-006 |
| [SL-116](SL-116-source-grabien.md) | Onboard Grabien | access_and_contract_gate | G2 | SL-003, SL-004, SL-006 |
| [SL-117](SL-117-source-aapb.md) | Onboard American Archive of Public Broadcasting | access_and_contract_gate | G2 | SL-003, SL-004, SL-006 |
| [SL-118](SL-118-source-cspan.md) | Onboard C-SPAN Video Library | access_and_contract_gate | G2 | SL-003, SL-004, SL-006 |
| [SL-119](SL-119-source-vanderbilt.md) | Onboard Vanderbilt Television News Archive | access_and_contract_gate | G2 | SL-003, SL-004, SL-006 |
| [SL-120](SL-120-source-google_fact_check.md) | Onboard Google Fact Check Tools API | access_and_contract_gate | G2 | SL-003, SL-004, SL-006 |
| [SL-121](SL-121-source-claimreview.md) | Onboard ClaimReview structured data | access_and_contract_gate | G2 | SL-003, SL-004, SL-006 |
| [SL-122](SL-122-source-fact_check_insights.md) | Onboard Fact-Check Insights | access_and_contract_gate | G2 | SL-003, SL-004, SL-006 |
| [SL-123](SL-123-source-media_vault.md) | Onboard MediaVault / MediaReview | access_and_contract_gate | G2 | SL-003, SL-004, SL-006 |
| [SL-124](SL-124-source-politifact.md) | Onboard PolitiFact | access_and_contract_gate | G2 | SL-003, SL-004, SL-006 |
| [SL-125](SL-125-source-punditfact.md) | Onboard PunditFact | access_and_contract_gate | G2 | SL-003, SL-004, SL-006 |
| [SL-126](SL-126-source-factcheck_org.md) | Onboard FactCheck.org | access_and_contract_gate | G2 | SL-003, SL-004, SL-006 |
| [SL-127](SL-127-source-reuters_fact_check.md) | Onboard Reuters Fact Check | access_and_contract_gate | G2 | SL-003, SL-004, SL-006 |
| [SL-128](SL-128-source-afp_fact_check.md) | Onboard AFP Fact Check | access_and_contract_gate | G2 | SL-003, SL-004, SL-006 |
| [SL-129](SL-129-source-media_matters.md) | Onboard Media Matters for America | access_and_contract_gate | G2 | SL-003, SL-004, SL-006 |
| [SL-130](SL-130-source-mrc.md) | Onboard Media Research Center | access_and_contract_gate | G2 | SL-003, SL-004, SL-006 |
| [SL-131](SL-131-source-newsbusters.md) | Onboard NewsBusters | access_and_contract_gate | G2 | SL-003, SL-004, SL-006 |
| [SL-132](SL-132-source-newsguard.md) | Onboard NewsGuard False Claim Fingerprints | access_and_contract_gate | G2 | SL-003, SL-004, SL-006 |
| [SL-133](SL-133-source-full_fact_ai.md) | Onboard Full Fact AI | access_and_contract_gate | G2 | SL-003, SL-004, SL-006 |
| [SL-134](SL-134-source-manual_import.md) | Onboard Authorized manual input | access_and_contract_gate | G2 | SL-003, SL-004, SL-006 |
| [SL-135](SL-135-source-tv_news_archive.md) | Onboard Internet Archive TV News Archive | access_and_contract_gate | G2 | SL-003, SL-004, SL-006 |
| [SL-136](SL-136-source-subject_social_accounts.md) | Onboard Subject-operated social media accounts | access_and_contract_gate | G2 | SL-003, SL-004, SL-006 |
| [SL-137](SL-137-source-subject_written_work.md) | Onboard Subject-authored columns, op-eds and newsletters | access_and_contract_gate | G2 | SL-003, SL-004, SL-006 |
| [SL-138](SL-138-source-podcasts_radio.md) | Onboard Podcast feeds and radio programs | access_and_contract_gate | G2 | SL-003, SL-004, SL-006 |
| [SL-139](SL-139-source-congress_gov.md) | Onboard Congress.gov API | access_and_contract_gate | G2 | SL-003, SL-004, SL-006, SL-014 |
| [SL-140](SL-140-source-govinfo.md) | Onboard GovInfo API | access_and_contract_gate | G2 | SL-003, SL-004, SL-006, SL-014 |
| [SL-141](SL-141-source-federal_register.md) | Onboard Federal Register API | access_and_contract_gate | G2 | SL-003, SL-004, SL-006, SL-014 |
| [SL-142](SL-142-source-bls.md) | Onboard Bureau of Labor Statistics Public Data API | access_and_contract_gate | G2 | SL-003, SL-004, SL-006, SL-014 |
| [SL-143](SL-143-source-census.md) | Onboard U.S. Census Bureau Data API | access_and_contract_gate | G2 | SL-003, SL-004, SL-006, SL-014 |
| [SL-144](SL-144-source-fred.md) | Onboard FRED (Federal Reserve Bank of St. Louis) API | access_and_contract_gate | G2 | SL-003, SL-004, SL-006, SL-014 |
| [SL-145](SL-145-source-openfec.md) | Onboard OpenFEC API | access_and_contract_gate | G2 | SL-003, SL-004, SL-006, SL-014 |
| [SL-146](SL-146-source-courtlistener.md) | Onboard CourtListener API | access_and_contract_gate | G2 | SL-003, SL-004, SL-006, SL-014 |
| [SL-147](SL-147-source-official_publications.md) | Onboard Other official agency, legislative and court publications | access_and_contract_gate | G2 | SL-003, SL-004, SL-006, SL-014 |
| [SL-201](SL-201-shared-claim-index-and-provenance-preserving-bulk-seeds.md) | Shared claim index and provenance-preserving bulk seeds | verified_local_reference | G3 | SL-001 |
| [SL-202](SL-202-revision-bound-evidence-cards-and-correction-blocking.md) | Revision-bound evidence cards and correction blocking | verified_local_reference | G3 | SL-201 |
| [SL-203](SL-203-confirmed-turn-event-deduplicated-phrase-profiles.md) | Confirmed-turn event-deduplicated phrase profiles | verified_local_reference | G3 | SL-001 |
| [SL-204](SL-204-incremental-profile-refresh-with-evaluation-exclusions.md) | Incremental profile refresh with evaluation exclusions | verified_local_reference | G3 | SL-203 |
| [SL-205](SL-205-caption-window-planner-and-shared-audio-interval-unions.md) | Caption window planner and shared audio interval unions | verified_local_reference | G3 | SL-203 |
| [SL-206](SL-206-official-typesafe-transport-and-bounded-model-orchestration.md) | Official TypeSafe transport and bounded model orchestration | verified_mock_contract | G2 | SL-205 |
| [SL-207](SL-207-raw-capture-and-quantization-aware-fault-handling.md) | Raw capture and quantization-aware fault handling | verified_mock_contract | G2 | SL-206 |
| [SL-208](SL-208-selective-media-execution-and-offset-preserving-manifests.md) | Selective media execution and offset-preserving manifests | verified_synthetic_media | G3 | SL-205 |
| [SL-209](SL-209-coverage-diagnostics-and-full-cost-comparison-tools.md) | Coverage diagnostics and full-cost comparison tools | verified_local_reference | G3 | SL-205 |
| [SL-210](SL-210-additive-database-migration-and-release-artifact-proof.md) | Additive database migration and release artifact proof | verified_local_reference | G3 | SL-201, SL-207 |
| [SL-211](SL-211-execute-authorized-pinned-jev-contract-acceptance.md) | Execute authorized pinned Jev contract acceptance | proposed | G2 | SL-206, SL-207 |
| [SL-212](SL-212-build-independently-labeled-cross-program-localization-corpus.md) | Build independently labeled cross-program localization corpus | proposed | G3 | SL-203, SL-205 |
| [SL-213](SL-213-validate-local-speaker-embeddings-and-target-speaker-detection.md) | Validate local speaker embeddings and target-speaker detection | proposed | G3 | SL-208, SL-212 |
| [SL-214](SL-214-fit-and-govern-event-held-out-localization-calibration.md) | Fit and govern event-held-out localization calibration | proposed | G3 | SL-211, SL-212, SL-213 |
| [SL-215](SL-215-benchmark-broad-paraphrase-retrieval-and-large-claim-storage.md) | Benchmark broad paraphrase retrieval and large claim storage | proposed | G3 | SL-201, SL-202 |
| [SL-216](SL-216-reconcile-edited-video-duplicates-and-uncertain-event-timelines.md) | Reconcile edited-video duplicates and uncertain event timelines | proposed | G3 | SL-008, SL-009, SL-205 |
| [SL-217](SL-217-connect-accepted-turn-events-to-scheduled-profile-proposals.md) | Connect accepted-turn events to scheduled profile proposals | proposed | G3 | SL-204, SL-017 |
| [SL-218](SL-218-complete-real-browser-validation-and-collaborative-review-ux.md) | Complete real browser validation and collaborative review UX | proposed | G3 | SL-205, SL-202 |
| [SL-219](SL-219-measure-and-route-by-all-in-processing-cost.md) | Measure and route by all-in processing cost | proposed | G3 | SL-209, SL-211, SL-213 |
| [SL-220](SL-220-purge-revoked-source-derived-profiles-and-provider-artifacts.md) | Purge revoked source-derived profiles and provider artifacts | proposed | G2 | SL-006, SL-207 |
| [SL-301](SL-301-bind-recovered-receipts-to-their-own-operation.md) | Bind recovered receipts to their own provider operation | ready_for_codex | G2 | SL-207 |

Machine index: [tickets.json](tickets.json). No remote issues were created. Local-reference, mocked-contract and synthetic-media statuses have different evidence meanings; none implies a completed real-source service.
