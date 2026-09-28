# Source matrix — every input retained

The registry contains **47 entries: 33 named sources/products/formats from the original discovery design, one manual input mode, and 13 added entries** — the Internet Archive TV News Archive, three first-party channels for statements the subject publishes directly, and nine `primary_evidence` sources used to check propositions rather than to find statements. Primary-evidence sources are queried from a proposition's scope, never from the subject's name. A source can be useful even when no bulk/API entitlement exists. `http_client` means code with mocked tests, not a live connection. `file_parser` means a documented shape has a parser with synthetic fixtures. `contract_only` means discovery/intake requirements, not a running integration. All sources are disabled by default; all live-connection flags remain false for this delivery.

A source collection and a schema format are deliberately distinct: ClaimReview is a format; Fact-Check Insights is a dataset; a publisher is an origin. Do not count them as independent evidence when they carry the same underlying article.

| ID | Name | Role | Access | Implemented surface | Worksheet |
|---|---|---|---|---|---|
| `youtube` | YouTube Data API | appearance_discovery | api_key | http_client | [Intake](sources/youtube.md) |
| `cnn_transcripts` | CNN program transcripts | transcript_discovery | publisher_terms | contract_only | [Intake](sources/cnn_transcripts.md) |
| `cbs_transcripts` | CBS program transcripts | transcript_discovery | publisher_terms | contract_only | [Intake](sources/cbs_transcripts.md) |
| `internet_archive` | Internet Archive | archive_discovery | public_api_item_rights | http_client | [Intake](sources/internet_archive.md) |
| `gdelt_tv` | GDELT Television Explorer | broadcast_discovery | public_interface | contract_only | [Intake](sources/gdelt_tv.md) |
| `gdelt_visual` | GDELT Visual Explorer | visual_discovery | public_interface | contract_only | [Intake](sources/gdelt_visual.md) |
| `gdelt_tv_ngrams` | GDELT Television Ngrams | frequency_signal | public_files | contract_only | [Intake](sources/gdelt_tv_ngrams.md) |
| `gdelt_gqg` | GDELT Global Quotation Graph | quotation_discovery | public_files | file_parser | [Intake](sources/gdelt_gqg.md) |
| `quotebank` | Quotebank | quotation_discovery | dataset_terms | file_parser | [Intake](sources/quotebank.md) |
| `media_cloud` | Media Cloud | article_discovery | api_credentials | contract_only | [Intake](sources/media_cloud.md) |
| `lexisnexis` | LexisNexis / Nexis Uni | licensed_transcripts | commercial | contract_only | [Intake](sources/lexisnexis.md) |
| `tveyes` | TVEyes | licensed_transcripts | commercial | contract_only | [Intake](sources/tveyes.md) |
| `critical_mention` | Critical Mention | licensed_transcripts | commercial | contract_only | [Intake](sources/critical_mention.md) |
| `sprinklr` | Sprinklr | monitoring | commercial | contract_only | [Intake](sources/sprinklr.md) |
| `snapstream` | SnapStream | authorized_capture | commercial | contract_only | [Intake](sources/snapstream.md) |
| `grabien` | Grabien | clip_discovery | commercial_or_publisher_terms | contract_only | [Intake](sources/grabien.md) |
| `aapb` | American Archive of Public Broadcasting | archive_discovery | public_metadata_restricted_transcripts | http_client | [Intake](sources/aapb.md) |
| `cspan` | C-SPAN Video Library | public_event_discovery | publisher_terms | contract_only | [Intake](sources/cspan.md) |
| `vanderbilt` | Vanderbilt Television News Archive | historical_discovery | research_loan | contract_only | [Intake](sources/vanderbilt.md) |
| `google_fact_check` | Google Fact Check Tools API | review_discovery | api_key | http_client | [Intake](sources/google_fact_check.md) |
| `claimreview` | ClaimReview structured data | review_format | publisher_terms | file_parser | [Intake](sources/claimreview.md) |
| `fact_check_insights` | Fact-Check Insights | review_discovery | registration_terms | file_parser | [Intake](sources/fact_check_insights.md) |
| `media_vault` | MediaVault / MediaReview | media_authenticity | registration_terms | contract_only | [Intake](sources/media_vault.md) |
| `politifact` | PolitiFact | review_discovery | publisher_terms | contract_only | [Intake](sources/politifact.md) |
| `punditfact` | PunditFact | review_discovery | publisher_terms | contract_only | [Intake](sources/punditfact.md) |
| `factcheck_org` | FactCheck.org | review_discovery | publisher_terms | contract_only | [Intake](sources/factcheck_org.md) |
| `reuters_fact_check` | Reuters Fact Check | review_discovery | publisher_terms | contract_only | [Intake](sources/reuters_fact_check.md) |
| `afp_fact_check` | AFP Fact Check | review_discovery | publisher_terms | contract_only | [Intake](sources/afp_fact_check.md) |
| `media_matters` | Media Matters for America | watchdog_leads | publisher_terms | contract_only | [Intake](sources/media_matters.md) |
| `mrc` | Media Research Center | watchdog_leads | publisher_terms | contract_only | [Intake](sources/mrc.md) |
| `newsbusters` | NewsBusters | watchdog_leads | publisher_terms | contract_only | [Intake](sources/newsbusters.md) |
| `newsguard` | NewsGuard False Claim Fingerprints | licensed_reviews | commercial | contract_only | [Intake](sources/newsguard.md) |
| `full_fact_ai` | Full Fact AI | workflow_comparator | commercial | contract_only | [Intake](sources/full_fact_ai.md) |
| `manual_import` | Authorized manual input | general_input | operator_verified | file_parser | [Intake](sources/manual_import.md) |
| `tv_news_archive` | Internet Archive TV News Archive | transcript_discovery | public_interface | contract_only | [Intake](sources/tv_news_archive.md) |
| `subject_social_accounts` | Subject-operated social media accounts | first_party_statements | platform_terms | contract_only | [Intake](sources/subject_social_accounts.md) |
| `subject_written_work` | Subject-authored columns, op-eds and newsletters | first_party_statements | publisher_terms | contract_only | [Intake](sources/subject_written_work.md) |
| `podcasts_radio` | Podcast feeds and radio programs | appearance_discovery | feed_or_broadcaster_terms | contract_only | [Intake](sources/podcasts_radio.md) |
| `congress_gov` | Congress.gov API | primary_evidence | api_key | contract_only | [Intake](sources/congress_gov.md) |
| `govinfo` | GovInfo API | primary_evidence | api_key | contract_only | [Intake](sources/govinfo.md) |
| `federal_register` | Federal Register API | primary_evidence | public_api | contract_only | [Intake](sources/federal_register.md) |
| `bls` | Bureau of Labor Statistics Public Data API | primary_evidence | public_api | contract_only | [Intake](sources/bls.md) |
| `census` | U.S. Census Bureau Data API | primary_evidence | public_api | contract_only | [Intake](sources/census.md) |
| `fred` | FRED (Federal Reserve Bank of St. Louis) API | primary_evidence | api_key | contract_only | [Intake](sources/fred.md) |
| `openfec` | OpenFEC API | primary_evidence | api_key | contract_only | [Intake](sources/openfec.md) |
| `courtlistener` | CourtListener API | primary_evidence | api_token | contract_only | [Intake](sources/courtlistener.md) |
| `official_publications` | Other official agency, legislative and court publications | primary_evidence | publisher_terms | contract_only | [Intake](sources/official_publications.md) |

## First-party reference checks

See [research notes](RESEARCH_NOTES.md). Public documentation was inspected for selected APIs, formats and speech libraries. Runtime downloads were not verified because outbound DNS failed. Commercial accounts, restricted transcripts, and historical completeness were not tested. Registry `reviewed_on` is the date the entry was reviewed, not a blanket statement that every linked site/API was successfully retrieved.
