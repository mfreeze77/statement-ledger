## 04. Domain model and invariants

### 04.1 Identity, presence, and the event/asset distinction

`Person` is the stable subject identity, not a transcript label. `Event` is an original
program, interview, panel, speech, or other communication event. `Appearance` links a
person to an event and records whether they were a candidate, confirmed, mentioned only,
or rejected. `Asset` is a particular recording, upload, excerpt, or copy. Several assets
may represent one event. A montage can require several event mappings; the single-event
asset model in v0.1 is deliberately insufficient for arbitrary montages and must not be
used to force a false one-event assignment.

An event contains references to observations that establish it. An appearance contains
its own supporting observations and explicit review. An asset contains its source
observation, rights grant, duration, URL, role, optional byte hash, and optionally a
reviewed constant offset into the original event timeline. Original/copy labels alone
do not perform deduplication; the alignment must be justified.

### 04.2 Transcript and utterance records

A `Transcript` belongs to exactly one asset and contains ordered, timed segments. Every
segment has integer-millisecond start/end positions, a local speaker label, retained
text, and an overlap flag. End must exceed start and fit within the asset duration.
Segments may overlap where the source warrants it; overlap cannot be silently flattened.
Word-level timing is a target extension. The reference ASR importer retains segment
precision even if the source engine is capable of more precise alignment.

A `SpeakerMapping` is scoped to one transcript revision and one local label. A confirmed
mapping requires reviewed evidence and cannot duplicate an existing confirmed mapping
for that same label in that same transcript. The reserved unassigned/unknown labels
cannot be confirmed as a person. Audio must first be separated into meaningful local
speaker labels, whether by diarization or manual segmentation.

An `Utterance` selects a contiguous range of segments from one transcript, references the
speaker mapping and appearance, and stores exact text. The service checks that every
selected segment belongs to the mapped label, that the appearance matches the person
and event, and that the retained words exactly match the source segments joined with
spaces. Acceptance requires reviewed context and identity; unresolved overlapping speech
blocks acceptance. Non-contiguous words cannot be assembled into a misleading quote.

### 04.3 Propositions and occurrences

A `Proposition` represents a scoped claim, not a soundbite. Its kind distinguishes an
empirical claim, prediction, opinion, or ambiguity. Its scope includes entity, metric,
geography, period, unit, baseline, comparator, quantity, and definition. Unknown scope
is allowed during extraction but must not be silently treated as a wildcard during
review matching. An explicit `not_applicable` value can be used when a field is truly
inapplicable and the reviewer has checked that interpretation.

An `Occurrence` connects a proposition to an utterance and records the speech act:
asserted, quoted, rejected, hypothetical, question, or unclear. Only a reviewed assertion
can enter the eligible assertion-occurrence view. Repeated assertion occurrences can
reference one proposition. A paragraph containing several factual assertions can produce
several propositions. Paraphrase similarity is not a permission to merge their scope.

### 04.4 Evidence and reviews

`Evidence` points to a retained source observation, an exact excerpt, a locator, the
proposition it bears on, a relationship such as support/conflict/context, a source type,
and an applicable scope. The excerpt must occur in retained source text. External-review
observations cannot be relabeled as primary evidence. A generic manual observation still
requires the operator to establish why it is primary; structural validation is not an
automatic source-authenticity judgment.

A `Review` references one proposition, one or more reviewed asserted occurrences, and
its evidence records. A completed factual finding requires reviewer attribution, a review
time, explicit scope review, underlying primary evidence, and relationship compatibility.
Supported, contradicted, mixed, unresolved, and not-checkable are claim-level outcomes,
not person categories. The code checks structural prerequisites; it does not prove the
reviewer's reasoning. Each outcome must retain an explanation and limitations.

### 04.5 Corrections, coverage, and revisions

`Correction` points to a target and a source observation, preserving a reported or
verified correction with reviewer attribution where required. `CoverageRun` captures the
person, source, query, window, counts, cursor, state, and limitations. Query completion
is not corpus completion. Native JSON Schemas are generated for these 15 implemented
record kinds and are the exact v0.1 request contracts.

Every stored record revision has an ID, revision number, payload hash, dependency
revision snapshot, timestamp, and actor. Current heads may be stale. Rewriting a parent
marks descendants stale. Revalidation against unchanged content still records updated
dependency revisions when needed. The service rejects dependency cycles and updates
that do not supply the current expected revision.

### 04.6 Target extensions, not current record types

The target adds Investigation, DiscoveryEdge, AcquisitionReceipt, TimeFact, MediaTrack,
PiecewiseAlignment, WordToken, IdentityEvidence, ContextBundle, ClaimCandidate,
PropositionEquivalenceProposal, OccurrenceEquivalence, ReviewResolution, CorrectionCase,
PublicationSnapshot, RetentionTombstone, ProviderRun, CostReservation, and EvaluationCase.
Each extension must cite its parent revisions and preserve the same uncertainty rules.
Adding a name to this list does not create a working API. Implement these through
explicit schema versions, migrations, source fixtures, and contract tests.
