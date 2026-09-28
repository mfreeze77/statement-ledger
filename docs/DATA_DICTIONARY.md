# Implemented data dictionary — v0.2

Source of truth: `src/statement_ledger/models.py` and `acceleration_models.py`. The 20 record kinds below match generated JSON Schemas. Cross-record approval, scope, rights, freshness, and provenance rules remain service checks, not schema guarantees.

Every write has an append-only revision envelope and dependency snapshots. A revision alone is not independent proof of source authenticity. Unknown scope fields retain their uncertainty; stale records cannot silently regain approval.

## `person` — Person

| Field | Required | Shape / constraints |
|---|---|---|
| `id` | no | `{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"}` |
| `display_name` | yes | `{"maxLength":250,"minLength":1,"type":"string"}` |
| `aliases` | no | `{"items":{"type":"string"},"maxItems":50,"type":"array"}` |
| `identity_urls` | no | `{"items":{"type":"string"},"maxItems":30,"type":"array"}` |
| `synthetic` | no | `{"default":false,"type":"boolean"}` |

Nested definitions: [JSON Schema](../contracts/person.schema.json). Source dependencies and transition rules are enforced by the ledger service.

## `rights` — RightsGrant

| Field | Required | Shape / constraints |
|---|---|---|
| `id` | no | `{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"}` |
| `source_id` | yes | `{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"}` |
| `basis` | yes | `{"maxLength":100000,"minLength":1,"type":"string"}` |
| `allowed` | no | `{"items":{"enum":["discover","store_text","store_media","process_audio","derive_clip","publish_excerpt","publish_media","send_to_provider","index_external","learn_profile","process_biometrics"],"type":"string"},"type":"array"}` |
| `evidence_url` | no | `{"anyOf":[{"type":"string"},{"type":"null"}],"default":null}` |
| `expires_at` | no | `{"anyOf":[{"format":"date-time","type":"string"},{"type":"null"}],"default":null}` |
| `reviewed_by` | yes | `{"type":"string"}` |

Nested definitions: [JSON Schema](../contracts/rights.schema.json). Source dependencies and transition rules are enforced by the ledger service.

## `observation` — Observation

| Field | Required | Shape / constraints |
|---|---|---|
| `id` | no | `{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"}` |
| `source_id` | yes | `{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"}` |
| `native_id` | yes | `{"maxLength":100000,"minLength":1,"type":"string"}` |
| `rights_id` | yes | `{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"}` |
| `kind` | yes | `{"enum":["appearance_lead","quotation_lead","external_review","media_review","transcript_lead","frequency_signal","metadata","primary_document"],"type":"string"}` |
| `url` | yes | `{"type":"string"}` |
| `title` | no | `{"default":"","type":"string"}` |
| `text` | no | `{"anyOf":[{"type":"string"},{"type":"null"}],"default":null}` |
| `reported_speaker` | no | `{"anyOf":[{"type":"string"},{"type":"null"}],"default":null}` |
| `published_at` | no | `{"anyOf":[{"type":"string"},{"type":"null"}],"default":null}` |
| `links` | no | `{"items":{"type":"string"},"maxItems":10000,"type":"array"}` |
| `raw_payload` | yes | `{"additionalProperties":true,"type":"object"}` |
| `retrieved_at` | no | `{"format":"date-time","type":"string"}` |
| `raw_sha256` | yes | `{"pattern":"^[a-f0-9]{64}$","type":"string"}` |
| `parser_version` | no | `{"default":"1","type":"string"}` |

Nested definitions: [JSON Schema](../contracts/observation.schema.json). Source dependencies and transition rules are enforced by the ledger service.

## `event` — Event

| Field | Required | Shape / constraints |
|---|---|---|
| `id` | no | `{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"}` |
| `title` | yes | `{"maxLength":100000,"minLength":1,"type":"string"}` |
| `occurred_at` | no | `{"anyOf":[{"type":"string"},{"type":"null"}],"default":null}` |
| `date_precision` | no | `{"default":"unknown","enum":["unknown","year","month","day","instant"],"type":"string"}` |
| `observation_ids` | yes | `{"items":{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"},"minItems":1,"type":"array"}` |
| `date_evidence` | no | `{"anyOf":[{"type":"string"},{"type":"null"}],"default":null}` |
| `synthetic` | no | `{"default":false,"type":"boolean"}` |

Nested definitions: [JSON Schema](../contracts/event.schema.json). Source dependencies and transition rules are enforced by the ledger service.

## `appearance` — Appearance

| Field | Required | Shape / constraints |
|---|---|---|
| `id` | no | `{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"}` |
| `event_id` | yes | `{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"}` |
| `person_id` | yes | `{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"}` |
| `observation_ids` | yes | `{"items":{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"},"minItems":1,"type":"array"}` |
| `status` | no | `{"default":"candidate","enum":["candidate","confirmed","mentioned_only","rejected"],"type":"string"}` |
| `reviewer` | no | `{"anyOf":[{"type":"string"},{"type":"null"}],"default":null}` |
| `rationale` | no | `{"anyOf":[{"type":"string"},{"type":"null"}],"default":null}` |

Nested definitions: [JSON Schema](../contracts/appearance.schema.json). Source dependencies and transition rules are enforced by the ledger service.

## `asset` — Asset

| Field | Required | Shape / constraints |
|---|---|---|
| `id` | no | `{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"}` |
| `event_id` | yes | `{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"}` |
| `observation_id` | yes | `{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"}` |
| `rights_id` | yes | `{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"}` |
| `url` | yes | `{"type":"string"}` |
| `role` | no | `{"default":"unknown","enum":["original","copy","excerpt","unknown"],"type":"string"}` |
| `duration_ms` | yes | `{"minimum":0,"type":"integer"}` |
| `content_sha256` | no | `{"anyOf":[{"pattern":"^[a-f0-9]{64}$","type":"string"},{"type":"null"}],"default":null}` |
| `event_offset_ms` | no | `{"anyOf":[{"type":"integer"},{"type":"null"}],"default":null}` |
| `alignment_reviewed_by` | no | `{"anyOf":[{"type":"string"},{"type":"null"}],"default":null}` |
| `alignment_evidence` | no | `{"anyOf":[{"type":"string"},{"type":"null"}],"default":null}` |
| `published_at` | no | `{"anyOf":[{"type":"string"},{"type":"null"}],"default":null}` |

Nested definitions: [JSON Schema](../contracts/asset.schema.json). Source dependencies and transition rules are enforced by the ledger service.

## `transcript` — Transcript

| Field | Required | Shape / constraints |
|---|---|---|
| `id` | no | `{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"}` |
| `asset_id` | yes | `{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"}` |
| `engine` | yes | `{"maxLength":100000,"minLength":1,"type":"string"}` |
| `language` | no | `{"default":"en","type":"string"}` |
| `segments` | yes | `{"items":{"$ref":"#/$defs/Segment"},"maxItems":100000,"minItems":1,"type":"array"}` |
| `model_revision` | no | `{"anyOf":[{"type":"string"},{"type":"null"}],"default":null}` |
| `input_sha256` | no | `{"anyOf":[{"pattern":"^[a-f0-9]{64}$","type":"string"},{"type":"null"}],"default":null}` |
| `precision` | no | `{"default":"segment","enum":["segment","word","manual"],"type":"string"}` |

Nested definitions: [JSON Schema](../contracts/transcript.schema.json). Source dependencies and transition rules are enforced by the ledger service.

## `speaker_mapping` — SpeakerMapping

| Field | Required | Shape / constraints |
|---|---|---|
| `id` | no | `{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"}` |
| `transcript_id` | yes | `{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"}` |
| `speaker_label` | yes | `{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"}` |
| `person_id` | yes | `{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"}` |
| `status` | no | `{"default":"candidate","enum":["candidate","confirmed","rejected"],"type":"string"}` |
| `evidence` | no | `{"items":{"type":"string"},"type":"array"}` |
| `reviewer` | no | `{"anyOf":[{"type":"string"},{"type":"null"}],"default":null}` |

Nested definitions: [JSON Schema](../contracts/speaker_mapping.schema.json). Source dependencies and transition rules are enforced by the ledger service.

## `utterance` — Utterance

| Field | Required | Shape / constraints |
|---|---|---|
| `id` | no | `{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"}` |
| `transcript_id` | yes | `{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"}` |
| `mapping_id` | yes | `{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"}` |
| `appearance_id` | yes | `{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"}` |
| `segment_indices` | yes | `{"items":{"minimum":0,"type":"integer"},"minItems":1,"type":"array"}` |
| `exact_text` | yes | `{"maxLength":100000,"minLength":1,"type":"string"}` |
| `status` | no | `{"default":"candidate","enum":["candidate","accepted"],"type":"string"}` |
| `context_reviewed` | no | `{"default":false,"type":"boolean"}` |
| `overlap_resolved` | no | `{"default":false,"type":"boolean"}` |
| `reviewer` | no | `{"anyOf":[{"type":"string"},{"type":"null"}],"default":null}` |

Nested definitions: [JSON Schema](../contracts/utterance.schema.json). Source dependencies and transition rules are enforced by the ledger service.

## `proposition` — Proposition

| Field | Required | Shape / constraints |
|---|---|---|
| `id` | no | `{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"}` |
| `seed_observation_ids` | no | `{"items":{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"},"maxItems":10000,"type":"array"}` |
| `text` | yes | `{"maxLength":100000,"minLength":1,"type":"string"}` |
| `kind` | no | `{"default":"empirical","enum":["empirical","prediction","opinion","ambiguous"],"type":"string"}` |
| `scope` | yes | `{"$ref":"#/$defs/Scope"}` |

Nested definitions: [JSON Schema](../contracts/proposition.schema.json). Source dependencies and transition rules are enforced by the ledger service.

## `occurrence` — Occurrence

| Field | Required | Shape / constraints |
|---|---|---|
| `id` | no | `{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"}` |
| `utterance_id` | yes | `{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"}` |
| `proposition_id` | yes | `{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"}` |
| `assertion` | yes | `{"enum":["asserted","quoted","rejected","hypothetical","question","unclear"],"type":"string"}` |
| `extraction_reviewed_by` | no | `{"anyOf":[{"type":"string"},{"type":"null"}],"default":null}` |
| `extraction_rationale` | no | `{"anyOf":[{"type":"string"},{"type":"null"}],"default":null}` |

Nested definitions: [JSON Schema](../contracts/occurrence.schema.json). Source dependencies and transition rules are enforced by the ledger service.

## `evidence` — Evidence

| Field | Required | Shape / constraints |
|---|---|---|
| `id` | no | `{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"}` |
| `observation_id` | yes | `{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"}` |
| `title` | yes | `{"maxLength":100000,"minLength":1,"type":"string"}` |
| `excerpt` | yes | `{"maxLength":100000,"minLength":1,"type":"string"}` |
| `locator` | yes | `{"maxLength":100000,"minLength":1,"type":"string"}` |
| `proposition_id` | yes | `{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"}` |
| `relation` | no | `{"default":"undetermined","enum":["supports","conflicts","context","undetermined"],"type":"string"}` |
| `source_type` | no | `{"default":"primary","enum":["primary","secondary","external_review"],"type":"string"}` |
| `applicable_scope` | yes | `{"$ref":"#/$defs/Scope"}` |
| `observed_at` | no | `{"format":"date-time","type":"string"}` |

Nested definitions: [JSON Schema](../contracts/evidence.schema.json). Source dependencies and transition rules are enforced by the ledger service.

## `review` — Review

| Field | Required | Shape / constraints |
|---|---|---|
| `id` | no | `{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"}` |
| `proposition_id` | yes | `{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"}` |
| `occurrence_ids` | yes | `{"items":{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"},"minItems":1,"type":"array"}` |
| `evidence_ids` | no | `{"items":{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"},"type":"array"}` |
| `status` | no | `{"default":"draft","enum":["draft","reviewed"],"type":"string"}` |
| `finding` | no | `{"default":"unresolved","enum":["supported","contradicted","mixed","unresolved","not_checkable"],"type":"string"}` |
| `rationale` | yes | `{"maxLength":100000,"minLength":1,"type":"string"}` |
| `reviewer` | no | `{"anyOf":[{"type":"string"},{"type":"null"}],"default":null}` |
| `reviewed_at` | no | `{"anyOf":[{"format":"date-time","type":"string"},{"type":"null"}],"default":null}` |
| `scope_reviewed` | no | `{"default":false,"type":"boolean"}` |
| `limitations` | no | `{"items":{"type":"string"},"type":"array"}` |

Nested definitions: [JSON Schema](../contracts/review.schema.json). Source dependencies and transition rules are enforced by the ledger service.

## `correction` — Correction

| Field | Required | Shape / constraints |
|---|---|---|
| `id` | no | `{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"}` |
| `target_kind` | yes | `{"type":"string"}` |
| `target_id` | yes | `{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"}` |
| `observation_id` | yes | `{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"}` |
| `text` | yes | `{"maxLength":100000,"minLength":1,"type":"string"}` |
| `status` | no | `{"default":"reported","enum":["reported","verified","resolved"],"type":"string"}` |
| `resolution` | no | `{"anyOf":[{"type":"string"},{"type":"null"}],"default":null}` |
| `resolved_at` | no | `{"anyOf":[{"format":"date-time","type":"string"},{"type":"null"}],"default":null}` |
| `reviewer` | no | `{"anyOf":[{"type":"string"},{"type":"null"}],"default":null}` |

Nested definitions: [JSON Schema](../contracts/correction.schema.json). Source dependencies and transition rules are enforced by the ledger service.

## `coverage_run` — CoverageRun

| Field | Required | Shape / constraints |
|---|---|---|
| `id` | no | `{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"}` |
| `person_id` | yes | `{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"}` |
| `source_id` | yes | `{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"}` |
| `query` | yes | `{"type":"string"}` |
| `period_start` | yes | `{"format":"date","type":"string"}` |
| `period_end` | yes | `{"format":"date","type":"string"}` |
| `retrieved` | no | `{"default":0,"minimum":0,"type":"integer"}` |
| `processed` | no | `{"default":0,"minimum":0,"type":"integer"}` |
| `state` | no | `{"default":"planned","enum":["planned","partial","finished_query","blocked","failed"],"type":"string"}` |
| `next_cursor` | no | `{"anyOf":[{"type":"string"},{"type":"null"}],"default":null}` |
| `limitation` | yes | `{"maxLength":100000,"minLength":1,"type":"string"}` |

Nested definitions: [JSON Schema](../contracts/coverage_run.schema.json). Source dependencies and transition rules are enforced by the ledger service.

## `speaker_profile` — SpeakerProfile

| Field | Required | Shape / constraints |
|---|---|---|
| `id` | no | `{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"}` |
| `person_id` | yes | `{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"}` |
| `example_ids` | no | `{"items":{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"},"maxItems":10000,"type":"array"}` |
| `background_ids` | no | `{"items":{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"},"maxItems":10000,"type":"array"}` |
| `config` | no | `{"$ref":"#/$defs/ProfileConfig"}` |
| `algorithm` | no | `{"const":"event-log-odds-v1","default":"event-log-odds-v1","type":"string"}` |
| `features` | no | `{"items":{"$ref":"#/$defs/PhraseFeature"},"maxItems":500,"type":"array"}` |
| `target_event_ids` | no | `{"items":{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"},"type":"array"}` |
| `background_event_ids` | no | `{"items":{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"},"type":"array"}` |
| `retained_example_ids` | no | `{"items":{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"},"type":"array"}` |
| `duplicate_example_ids` | no | `{"items":{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"},"type":"array"}` |
| `bindings` | no | `{"items":{"$ref":"#/$defs/RecordRef"},"type":"array"}` |
| `readiness` | no | `{"default":"cold_start","enum":["cold_start","research_ready"],"type":"string"}` |
| `limitations` | no | `{"items":{"type":"string"},"type":"array"}` |
| `calibration` | no | `{"const":"uncalibrated","default":"uncalibrated","type":"string"}` |

Nested definitions: [JSON Schema](../contracts/speaker_profile.schema.json). Source dependencies and transition rules are enforced by the ledger service.

## `localization_run` — LocalizationRun

| Field | Required | Shape / constraints |
|---|---|---|
| `id` | no | `{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"}` |
| `profile_id` | yes | `{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"}` |
| `transcript_id` | yes | `{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"}` |
| `asset_id` | yes | `{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"}` |
| `config` | yes | `{"$ref":"#/$defs/LocalizationConfig"}` |
| `duration_ms` | yes | `{"minimum":0,"type":"integer"}` |
| `windows` | yes | `{"items":{"$ref":"#/$defs/CandidateWindow"},"maxItems":5000,"type":"array"}` |
| `proposed_intervals` | yes | `{"items":{"$ref":"#/$defs/Interval"},"type":"array"}` |
| `selected_intervals` | yes | `{"items":{"$ref":"#/$defs/Interval"},"type":"array"}` |
| `unprocessed_intervals` | yes | `{"items":{"$ref":"#/$defs/Interval"},"type":"array"}` |
| `caption_gaps` | yes | `{"items":{"$ref":"#/$defs/Interval"},"type":"array"}` |
| `decision_run_ids` | no | `{"items":{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"},"maxItems":1000,"type":"array"}` |
| `fallback_reasons` | no | `{"items":{"type":"string"},"type":"array"}` |
| `bindings` | yes | `{"items":{"$ref":"#/$defs/RecordRef"},"type":"array"}` |
| `proposed_audio_ms` | yes | `{"minimum":0,"type":"integer"}` |
| `selected_audio_ms` | yes | `{"minimum":0,"type":"integer"}` |
| `audio_reduction_fraction` | yes | `{"maximum":1,"minimum":0,"type":"number"}` |
| `coverage_recall` | no | `{"default":null,"type":"null"}` |
| `identities_confirmed` | no | `{"const":false,"default":false,"type":"boolean"}` |
| `probability_calibrated` | no | `{"const":false,"default":false,"type":"boolean"}` |

Nested definitions: [JSON Schema](../contracts/localization_run.schema.json). Source dependencies and transition rules are enforced by the ledger service.

## `decision_run` — DecisionRun

| Field | Required | Shape / constraints |
|---|---|---|
| `id` | no | `{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"}` |
| `purpose` | yes | `{"enum":["speaker_localization","claim_matching"],"type":"string"}` |
| `request_hash` | yes | `{"pattern":"^[a-f0-9]{64}$","type":"string"}` |
| `model_requested` | yes | `{"maxLength":100000,"minLength":1,"type":"string"}` |
| `model_resolved` | no | `{"anyOf":[{"type":"string"},{"type":"null"}],"default":null}` |
| `question_version` | yes | `{"maxLength":100000,"minLength":1,"type":"string"}` |
| `questions` | yes | `{"additionalProperties":true,"type":"object"}` |
| `answers` | no | `{"additionalProperties":true,"type":"object"}` |
| `bindings` | yes | `{"items":{"$ref":"#/$defs/RecordRef"},"minItems":1,"type":"array"}` |
| `input_ids` | no | `{"items":{"type":"string"},"type":"array"}` |
| `state_sha256` | yes | `{"pattern":"^[a-f0-9]{64}$","type":"string"}` |
| `status` | yes | `{"enum":["available","unavailable"],"type":"string"}` |
| `error_code` | no | `{"anyOf":[{"type":"string"},{"type":"null"}],"default":null}` |
| `warnings` | no | `{"items":{"type":"string"},"type":"array"}` |
| `receipt_ids` | no | `{"items":{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"},"type":"array"}` |
| `latency_ms` | yes | `{"minimum":0,"type":"number"}` |
| `usage` | no | `{"additionalProperties":{"type":"integer"},"type":"object"}` |
| `captured_at` | yes | `{"format":"date-time","type":"string"}` |

Nested definitions: [JSON Schema](../contracts/decision_run.schema.json). Source dependencies and transition rules are enforced by the ledger service.

## `claim_family` — ClaimFamily

| Field | Required | Shape / constraints |
|---|---|---|
| `id` | no | `{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"}` |
| `title` | yes | `{"maxLength":100000,"minLength":1,"type":"string"}` |
| `description` | no | `{"default":"","type":"string"}` |
| `proposition_ids` | yes | `{"items":{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"},"maxItems":10000,"minItems":1,"type":"array"}` |
| `grouping_basis` | yes | `{"maxLength":100000,"minLength":1,"type":"string"}` |
| `reviewer` | yes | `{"maxLength":100000,"minLength":1,"type":"string"}` |
| `equivalence_asserted` | no | `{"const":false,"default":false,"type":"boolean"}` |

Nested definitions: [JSON Schema](../contracts/claim_family.schema.json). Source dependencies and transition rules are enforced by the ledger service.

## `claim_card` — ClaimCard

| Field | Required | Shape / constraints |
|---|---|---|
| `id` | no | `{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"}` |
| `proposition_id` | yes | `{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"}` |
| `review_ids` | yes | `{"items":{"maxLength":180,"minLength":1,"pattern":"^[a-zA-Z0-9_.:-]+$","type":"string"},"maxItems":1000,"minItems":1,"type":"array"}` |
| `valid_until` | yes | `{"format":"date-time","type":"string"}` |
| `freshness_rationale` | yes | `{"maxLength":100000,"minLength":1,"type":"string"}` |
| `approved_by` | yes | `{"maxLength":100000,"minLength":1,"type":"string"}` |
| `automatic_verdict_reuse` | no | `{"const":false,"default":false,"type":"boolean"}` |

Nested definitions: [JSON Schema](../contracts/claim_card.schema.json). Source dependencies and transition rules are enforced by the ledger service.
