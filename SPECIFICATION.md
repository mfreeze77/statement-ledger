# Statement Ledger — Complete Product and Engineering Specification

Specification 1.1 · Software 0.2.0 · 2026-09-27 · Standalone project

This file is generated from `docs/spec/`. Chapters 00–22 preserve the original design and historical v0.1 boundaries; chapters 23–28 and docs/IMPLEMENTATION_STATUS.md define this upgrade. Implementation status is explicit; target requirements are not claims of completed code.

## 00. Product definition, boundaries, and interpretation

### 00.1 The problem being solved

An appearance, a quotation, a transcript, a video upload, and a fact-check are different
observations of public communication. They are currently scattered across sources with
different coverage, timing, access, formats, and editorial selection. Statement Ledger
uses them as cooperating inputs to reconstruct an inspectable history of a person's
public statements. The system starts from a subject and a declared research scope. It
follows leads into original events, locates speaking turns, preserves exact words and
context, separates propositions from their occurrences, and attaches documented evidence
and review history without rewriting the source record.

The product is not an article aggregator with a name filter. Its central value is the
ability to open a statement and reconstruct why the system associates those words with
that speaker, which event they belong to, which copies represent the same occurrence,
what question or qualification surrounded the words, and what evidence a reviewer used.

### 00.2 Independence is an architectural requirement

This is a new application with an independent repository, package namespace, source
registry, requirements, database, object storage, job state, API, user interface, model
configuration, deployment, security policy, and release history. No other private
application is a prerequisite, a system of record, or an implicit source of configuration.
No external project's ticket numbers, migrations, identifiers, tables, schemas, data,
credentials, or runtime imports belong in this repository. General design ideas may be
reused, but implementation decisions are made and tested here.

A future integration is a separately authorized adapter across a documented versioned
boundary. It must be removable without breaking local ingestion, review, or export.
The reference implementation has no mandatory external retrieval or model dependency.
The standalone namespace check in `scripts/check-standalone.py` guards against accidental
imports and configuration coupling. It is a regression check, not a complete static
proof of independence.

### 00.3 Primary users and jobs

The initial user is a single researcher operating a private workspace. Their jobs are to
scope an investigation, inspect coverage gaps, acquire permitted material, resolve an
appearance and speaker, review claim extraction, inspect evidence, record findings, and
correct mistakes. A source operator maintains connector credentials and contractual
limits. A reviewer checks context and evidence. In v0.1 these responsibilities may be
performed by one authenticated owner; they are not represented as independently verified
roles. Later collaborative releases must distinguish them through actual principals and
server-side permissions rather than trusting a supplied reviewer name.

The subject may be a pundit, interviewer, public official, expert, executive, or another
person making relevant public statements. The collection scope is public communication,
not private correspondence or surveillance of private life. The included Scott Jennings
configuration is a name-only discovery example. It does not assert current employment,
accounts, identities in recordings, statements, or findings. Synthetic fixtures use a
fictional speaker and are never merged into a real research workspace.

### 00.4 Required product outputs

The target product produces a source inventory, a coverage ledger, an original-event and
asset map, an attributed speaking-turn timeline, a statement ledger, scoped propositions,
assertion occurrence groups, evidence bundles, attributed external reviews, internal
review records, correction history, and provenance exports. Every summarized number must
be expandable to records and the eligibility rules that produced it. A collection with
no material is an empty or blocked collection, not evidence that the person never spoke.

The product must allow inspection without requiring a published conclusion. Unresolved
identity, incomplete context, inaccessible source material, conflicting evidence, and
unmatched quotations are valuable states. They must remain visible instead of being
converted into confident outputs merely to fill a dashboard.

### 00.5 Non-goals

There is no universal honesty score, inferred intent classifier, political endorsement,
character rating, fabricated certainty, or cross-person ranking. An inaccurate statement
and deliberate deception are different propositions. Source reputation and political
labels do not substitute for evidence about a particular claim. The system does not
promise access to all YouTube appearances, all historical broadcasts, or all statements.
It does not bypass platform access controls, acquire third-party media without approved
rights, or automatically redistribute full transcripts and recordings.

### 00.6 Specification versus implementation

**Target requirement** means the desired product behavior, not a completion claim.
**Implemented** means code exists and its stated local tests have been run.
**Mock-verified** means protocol behavior was exercised without a live provider.
**Access-dependent** means credentials, a license, or a verified export shape is missing.
**Planned** means the required code is not in v0.1. The status matrix and validation report
are authoritative. Listing a source in the registry never upgrades its implementation
status. The v0.1 deliverable is a runnable reference vertical slice with a full design and
backlog, not a fully deployed national-media monitoring service.


---

## 01. End-to-end workflows and user-visible states

### 01.1 Create a bounded investigation

The owner creates a subject, supplies reviewed aliases and public identity references
when available, and defines the date range, languages, source set, program/channel scope,
collection purpose, retention limits, permitted operations, budget, and publication mode.
Unknown values are explicit. An empty alias list is preferable to guessed aliases. Dates
must distinguish an intended investigation window from what the available sources can
actually cover. A query for an upload date is not an event-date filter.

The planner creates separate tasks for name searches, known-program inventory inspection,
quotation backtracking, and source-link expansion. Each task references the source,
query, scope revision, budget, cursor, execution state, and reason. Planning does not
execute a query or grant permission to acquire its results. In v0.1 the planner emits a
JSON plan; durable plan execution is a later milestone. Each explicit `discover` CLI
invocation has a page budget and writes a receipt with its remaining cursor.

### 01.2 From a quotation lead to a speaking turn

A quotation lead records its exact source wording, reported speaker, surrounding text,
source URL, original payload, parser version, and source-date interpretation. The next
step is to investigate the original appearance, not to mark the quote accepted. An
article may identify a program or date, embed a video, link a transcript, or cite an older
article. Each relationship is retained as a discovery edge in the target system, with
its source evidence. Name matching alone cannot prove identity or presence.

Once a plausible event and recording are found, the researcher opens sufficient context.
An existing transcript may locate an approximate window. The system processes that
window or the full authorized episode, resolves local speaker labels, and aligns the
statement to the recording. The original quotation remains a source observation; a new
utterance record holds the audiovisual or transcript-backed statement. A mismatch is
preserved as a mismatch. The source article is not silently corrected in place.

### 01.3 From a program inventory to additional statements

The researcher examines a relevant program's episode inventory even when titles do not
mention the subject. A program transcript, introduction, guest list, or reviewed source
can establish a candidate appearance. Processing the full permitted episode can reveal
speaking turns that no quotation database indexed. This path is necessary to reduce the
selection bias of collecting only controversial clips or prior fact-checks.

A source may return a mention without an appearance, an appearance without speech, an
embedded replay of an earlier appearance, or a montage containing several events. The
system must preserve those distinctions. The reference model includes candidate,
confirmed, mentioned-only, and rejected appearance states. More detailed presence and
replay relations are target extensions, not existing automatic classifications.

### 01.4 From accepted utterance to reviewed finding

An accepted utterance points to exact transcript segments and a reviewed mapping between
a local speaker label and a person. A candidate extractor may propose atomic claims and
scope fields. The reviewer confirms what the speaker asserted, quoted, denied, asked,
qualified, or predicted. A separate proposition is linked to an occurrence; neither the
video title nor the publisher's interpretation becomes the speaker's assertion.

Evidence search then finds potentially relevant primary documents and prior reviews.
The reviewer checks temporal, geographic, metric, entity, quantity, definition, and
baseline compatibility. Findings are recorded with their supporting references,
limitations, reviewer attribution, and effective date. Changing evidence, attribution,
or the proposition invalidates dependent results until they are revalidated. The
reference code implements structural gates and invalidation; it does not autonomously
research or decide factual correctness.

### 01.5 Correct a mistake

The owner can report a misattribution, transcript error, alignment error, misleading
excerpt, duplicate occurrence, evidence revision, or a subject's clarification. Preserve
the prior record and the correction source. Review whether the correction changes the
source words, interpretation, evidence, or only a display detail. Create a new revision
rather than editing history. Dependent records become stale and must be explicitly
revalidated against current parents. The target workflow adds correction triage,
resolution status, affected-publication withdrawal, and acknowledgements.

In v0.1 correction records can be stored and inspected. A correction record alone does
not execute a semantic repair or resolve an appeal. Updating the affected record drives
the implemented invalidation mechanism. This distinction must remain visible to operators.

### 01.6 Standard states for work, not moral judgments

An item can be discovered, blocked-by-access, acquired, parse-failed, candidate,
needs-identity-review, needs-context, needs-alignment, accepted, needs-claim-review,
needs-evidence, reviewed, stale, withdrawn, or archived. These are workflow states.
Source failure does not become a claim finding. A prediction not yet due does not become
a false claim. A recording unavailable to the system does not prove absence of speech.
The user interface must show the next actionable reason, not a generic red failure badge.


---

## 02. Source strategy, registry, and connector contract

### 02.1 Every discovered source remains represented

The source registry covers YouTube; CNN and CBS transcripts; Internet Archive; GDELT
Television Explorer, Visual Explorer, television ngrams, and Global Quotation Graph;
Quotebank; Media Cloud; LexisNexis/Nexis Uni; TVEyes; Critical Mention; Sprinklr;
SnapStream; Grabien; AAPB; C-SPAN; Vanderbilt; Google Fact Check Tools; ClaimReview;
Fact-Check Insights; MediaVault/MediaReview; PolitiFact; PunditFact; FactCheck.org;
Reuters Fact Check; AFP Fact Check; Media Matters; Media Research Center; NewsBusters;
NewsGuard; and Full Fact AI. Authorized manual input supplies a common pathway for
sources whose dedicated transport or format has not yet been verified.

The registry also covers the Internet Archive TV News Archive's caption search, which is
distinct from the general Internet Archive metadata interface and underlies GDELT
Television Explorer; a segment found through both is one lead, not two. Statements the
subject publishes directly are first-party inputs: subject-operated social media accounts,
bylined columns, op-eds and newsletters, and podcast and radio appearances. The subject's
own video channel is collected through the YouTube source. First-party publication still
requires reviewed account ownership or bylines; an impersonation account, a reposted
item, or a publisher-written headline is not the subject's assertion.

A separate `primary_evidence` role holds sources used to check a proposition rather than
to find statements: Congress.gov, GovInfo, the Federal Register, the Bureau of Labor
Statistics, the Census Bureau, FRED, OpenFEC, CourtListener, and a catch-all for other
official publications entered through the manual envelope. These are queried from an
extracted proposition's scope (date, geography, quantity, definition, document version),
never from the subject's name, and the person planner marks them `claim_driven`. A
retrieved record bears on a proposition; it is not a finding. Retrieval, snapshotting and
exact locators are specified by SL-014.

These are not equivalent products. ClaimReview is a vocabulary. AAPB is an archive.
Full Fact AI is a workflow product. Some sources produce citations, some provide
metadata, some permit transcript delivery, and some provide licensed content only.
Their roles cannot be inferred from a count of names in the registry.

### 02.2 Registry fields

Each entry has a stable source ID, human-readable name, role, access class, implementation
class, parser key or null, documentation URLs, known limitations, next integration step,
review date, default enabled state, and live-verification state. All connectors are
disabled by default. Production extensions add contract version, allowed hostnames,
authentication profile reference, supported languages, coverage intervals, source-date
semantics, retention rules, cost unit, and supported discovery/acquisition operations.
Secrets are never stored in a registry object. Schema versions and legal permissions are
separate: a valid response shape does not grant storage or redistribution rights.

### 02.3 Required input envelope

The common source envelope records `source_id`, `native_id`, source URL, source-provided
title, observation kind, optional quoted/transcript text, reported speaker if any,
publication date only when its meaning is known, discovery links, raw payload, payload
hash, parser version, retrieval time, and rights-grant reference. The raw file archive
also records a byte-level SHA-256. A normalized-payload hash is not a substitute for the
hash of the original compressed file. Both serve different reproducibility needs.

The contract accepts observation kinds such as appearance lead, quotation lead, external
review, media review, transcript lead, frequency signal, metadata, and primary document.
No parser may emit a confirmed person-to-voice mapping, accepted utterance, or completed
internal review merely because an upstream record uses a speaker name or verdict label.

### 02.4 Transport behavior

A network connector has explicit authentication, endpoint, timeout, retry, pagination,
size, and budget boundaries. It preserves the input cursor and next cursor. A retry must
not double-count a successful page. Repeated cursors and inconsistent request identities
stop the run for inspection. Authorization errors are not retried blindly. Quota and
transient errors use a bounded delay. Error messages must not include credential-bearing
URLs or upstream bodies. Redirect behavior is explicit. The v0.1 JSON clients use fixed
HTTPS origins, reject redirects, cap decompressed response bytes, and do not fetch URLs
found inside results.

YouTube's official documentation describes paginated search and notes incomplete/index-
dependent results; channel uploads can be inspected through upload playlists. Caption
download has a different authorization requirement. Discovery metadata is therefore not
an implicit media-acquisition channel. References: [YouTube search](https://developers.google.com/youtube/v3/docs/search/list),
[caption download](https://developers.google.com/youtube/v3/docs/captions/download),
and [developer policies](https://developers.google.com/youtube/terms/developer-policies).

### 02.5 File parsing behavior

File parsers support bounded line-delimited UTF-8 records, gzip and bzip2 compression,
source-native JSON, explicit field validation, and error receipts. Large JSONL inputs
are streamed rather than loaded into memory. Root arrays in v0.1 are limited to 64 MiB
decompressed; larger arrays need a streaming converter or a future array-streaming
adapter. A record limit is a workload boundary, not evidence of corpus completion.
Malformed rows are retained through the source archive and reported with location.
Schema drift must be quarantined, not silently interpreted as an empty successful run.

GDELT documents per-minute compressed JSONL with nested quotations and surrounding
snippets. Quotebank documents both aggregated quotation-centric and article-centric
representations. v0.1 supports the quotation-centric variant only. Their source dates
are not automatically converted into event or publication dates. References:
[GDELT GQG](https://blog.gdeltproject.org/announcing-the-global-quotation-graph/),
[Quotebank schema](https://zenodo.org/records/4277311).

### 02.6 Commercial and publisher connectors

For a commercial source, obtain an actual sample export, endpoint specification,
retention/derivation rights, authentication method, stable record identifiers, timebase,
coverage statement, and backfill limits before implementation. A generic guessed REST
adapter is not an acceptable substitute. For publisher HTML, prefer authorized exports
or structured records; use robust parsing only after permission and samples are recorded.
Manual input must retain the actual source ID, not disguise all material as user-created.
The source-specific worksheets and source matrix define the next action for each entry.


---

## 03. Acquisition, provenance, and rights

### 03.1 Discovery and acquisition are separate operations

A search result may identify a recording without providing authorized bytes. The
acquisition stage accepts only approved source operations: a permitted archive file,
a publisher export, a licensed vendor delivery, owner-supplied media, or another
explicitly reviewed path. A content URL is evidence of location, not permission.
For unavailable media, preserve a reference and access state. Do not produce fabricated
clips, transcripts, or timestamps to compensate for an inaccessible source.

The reference network clients retrieve structured metadata/search responses only.
The media utilities operate on explicit local files. There is no general-purpose
YouTube downloader, arbitrary-URL media fetcher, or credentials-bypassing scraper.
A future acquisition worker must be separately sandboxed and permitted per source.

### 03.2 Rights-grant contract

An approved grant states the source, basis, supporting reference, reviewer, expiry if
applicable, and allowed operations. Operations are distinct: discovery, text storage,
media storage, audio processing, clip derivation, excerpt publication, media publication,
sending to a provider, and external indexing. The absence of an operation means it is
not allowed. An empty grant can be stored as a draft configuration but authorizes no
processing. A grant for one source cannot authorize another source automatically.

The target model adds asset/collection scope, jurisdiction, contractual volume limits,
retention deadline, model-training restrictions, subprocessor restrictions, permitted
publication destinations, and termination handling. v0.1 grants are source-scoped and
operator-attested. They are not a legal-permission verifier. An operator must ensure
the stated scope applies to the actual material. Commercial use or redistribution
questions require reviewing the applicable agreement, not extrapolating from this code.

### 03.3 Provenance layers

A source response has a retrieval timestamp, request identity without secrets, source
URL, source-native ID, transport status, and original bytes when retention is permitted.
A parser output has an input artifact hash, parser version, field mapping, normalized
payload hash, source-record locator, and any warnings. A transcript has the input asset,
engine/model information, language, timing precision, and revision. A speaking-turn
mapping has the supporting identity evidence and reviewer. A review has the precise
proposition, occurrence and evidence revisions it relied on.

The reference `Observation.raw_sha256` hashes canonical JSON, while `ingest_file` retains
and hashes the original input file bytes. These hashes answer different questions.
The target receipt store must link every output observation to its raw artifact and
record position. In v0.1 the CLI returns that file receipt, while the raw observation
contains its native payload; automatic receipt-to-observation indexing is a backlog item.

### 03.4 Four different clocks must not collapse

At minimum preserve event time, upload/publication time, provider-index/first-seen time,
and retrieval time. Review time is another independent clock. A 2026 upload can contain
a 2018 interview. GDELT's `date` is an observed-source timestamp, not proof of when the
speaker spoke. Quotebank's aggregated date describes an earliest article occurrence,
not an original recording date. An archive's generic `date` needs source-specific
interpretation. Unknown event time remains unknown, with optional date precision and
supporting evidence when a reviewer resolves it.

In v0.1 event dates require declared precision and a rationale, but a full temporal
hypothesis object is not implemented. Source dates that cannot safely be called
publication dates remain in raw payloads. Never fill missing event time from upload
metadata simply to make sorting easier.

### 03.5 Revisions and source disappearance

Raw objects are content-addressed and not overwritten by parser revisions. If a source
changes, preserve the old source revision and record a new one. If access expires or
content disappears, retain only material still allowed under the applicable policy.
A source tombstone records availability changes without pretending a withdrawn document
never existed. Public links and excerpts must be withdrawn when required, while the
minimum permitted audit trail is maintained. Automated retention/tombstone processing
is specified but not shipped in v0.1.

The application checks whether referenced grants are expired when writing dependent
records and when building eligible assertion views. Expiry does not automatically erase
stored files in the reference implementation. Production use requires the retention
worker and an audited deletion/withdrawal policy before ingesting restricted collections.

### 03.6 Integrity is not authenticity

The revision store's hashes and audit chain detect inconsistent changes under the
application's threat model. They do not prove a recording is genuine, establish that a
speaker said something, prove the date of acquisition, or resist an administrator who
rewrites the whole database and hash chain. A production deployment may checkpoint
signed manifests externally and use immutable object retention where appropriate.
Source authenticity, legal access, speaker identity, and byte integrity remain distinct
claims with distinct evidence.


---

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


---

## 05. Discovery expansion and coverage accounting

### 05.1 Four complementary discovery strategies

**Name-first discovery** searches a reviewed set of names and aliases. **Program-first
discovery** examines relevant episode/channel inventories and transcripts even when a
subject is absent from titles. **Quote-first discovery** traces quotation text and
context back to an event. **Link-first discovery** follows references, embeds, cited
transcripts, and original-media links found by any other strategy. These strategies
feed one another through explicit source observations; none is treated as a complete
universe on its own.

A query plan is versioned. It contains subject identity references, date basis, sources,
languages, positive and disambiguation terms, known program/channel IDs, quoted phrases,
search intent, and budget. Source syntax is generated by the source adapter. The canonical
plan must not assume all vendors support the same boolean syntax or date filtering.
Unknown accounts and channels remain candidate configuration, not verified identifiers.

### 05.2 Candidate appearance resolution

For each candidate, preserve why it was found: a name in a title, a transcript speaker
label, a guest list, an article quote, an embedded recording, or another source signal.
The resolver distinguishes person present and speaking, present but not speaking,
mentioned only, quoted by somebody else, archival replay, impersonation/satire, and
unresolved. The v0.1 appearance enum is smaller; additional distinctions belong in the
target PresenceEvidence model rather than arbitrary metadata that changes meaning.

The same textual name may identify multiple people. Resolution must use reviewed
context, not the largest online profile. A source claiming a particular person appeared
is evidence to inspect, not a sufficient reason to attach all words in a clip to them.
Disambiguation evidence must be retained so future identity corrections can invalidate
the affected material.

### 05.3 Discovery graph and bounded expansion

The target discovery graph has typed edges such as cites, embeds, quotes, identifies-
program, references-earlier-event, mirrors, excerpt-of, and possible-same-event. Edges
point to the source observation that supports them. A candidate link is not traversed
until its host, source rules, budget, and scope are approved. The frontier deduplicates
by source-native resource identity and normalized candidate URL while preserving every
raw URL and discovery path.

Expansion has explicit maximum depth, pages per source, records per run, bytes, event
window, source domains, retries, and spend. A discovered unexpected host returns to an
approval queue; a source document cannot authorize an agent to browse arbitrary URLs.
The model may propose discovery tasks but cannot change budgets, access policy, or
execution state. The v0.1 planner is deterministic and non-executing. Automatic frontier
execution is a later gate with a queue, source tests, and budget enforcement.

### 05.4 Inventory and coverage are separate from findings

Track source queries planned, attempted, succeeded, blocked, partially read, and exhausted;
results returned; unique candidate resources; confirmed appearances; accessible assets;
processed minutes; accepted target-speaker minutes; unresolved identity/context; reviewed
claims; and failed work by reason. Preserve source-specific start/end coverage and
retention gaps. A vendor outage, expired credential, empty result, and no configured
source are different conditions. A denominator cannot silently shrink because difficult
records failed to parse.

Coverage is a matrix of subject, source, time window, strategy, and processing stage.
An operator should be able to explain what was searched and why an item was excluded.
"All available appearances" is only acceptable with a defined inventory and a documented
meaning of available. It is not an appropriate label for a set assembled from web search
and watchdog clips. The reference UI says identified records only and displays exclusions.

### 05.5 Selection and measurement discipline

Start with systematic available-program collection when the objective is a broad speaking
record. Prior fact-checks and watchdog articles are valuable lead sources but are
editorially selected. Do not interpret their selection frequency as a person's frequency
of inaccurate speech. If a study uses a sample, store its sampling rule and stratum
before reviewing results. Preserve unreviewed material and disclose missing source
classes. A reviewed subset may support a statement about that subset, not an estimate
about every statement the person has ever made.

Compare coverage changes across runs separately from factual findings. New sources may
increase the number of known statements without any change in the subject's behavior.
A correction may reduce current reviewed counts while leaving historical published
snapshots explainable. These are data-lineage effects that the dashboard must surface.


---

## 06. Media processing, timelines, and clipping

### 06.1 Preserve originals and probe before processing

An authorized asset is identified by retained source reference and, when local bytes
are used, a byte-level checksum. Record duration, container, audio/video tracks, sample
rate, channels, frame-rate/timebase information, and probe-tool version. Derivatives
never overwrite originals. The v0.1 CLI requires a registered asset checksum before
processing local media; matching it is a lineage check, not independent proof of rights.
Content acquisition and media probing are planned as durable jobs rather than API-thread
work in the production architecture.

Malformed media is untrusted input. The target worker has a bounded local input root,
no unrestricted network access, resource limits, a read-only source mount, controlled
output location, protocol restrictions, and explicit timeouts. The reference FFmpeg
utility restricts paths to a configured root and avoids shell interpolation, but it is
not a complete hardened decoder sandbox. Do not expose arbitrary media upload and
processing publicly until the worker-isolation gate is complete.

### 06.2 Locate broadly before clipping narrowly

An article quote or caption hit proposes a time window, not necessarily the final
utterance boundary. Start with generous context, identify the surrounding question and
responses, and process the full available episode when justified by the investigation.
Clipping every search hit first can remove qualifications and cause repeated ASR work.
Cache derivations by original asset hash, time window, model/configuration revision,
and preprocessing parameters. Never share a cache entry across unequal timebases or
rights partitions solely because the same words occur.

The reference `clip_plan` uses integer milliseconds and a configurable context padding,
defaulting to 15 seconds. That is an initial utility parameter, not a rule that 15 seconds
always preserves sufficient context. A question may begin minutes earlier. The target
ContextBundle stores explicit relationships to surrounding turns rather than only a
fixed padding number.

### 06.3 Separate source coordinates and event coordinates

Every timestamp has a coordinate system. Source time belongs to a particular media
asset. Event time belongs to the resolved original appearance. A derived excerpt can
start at source zero while corresponding to event time 20 seconds. In the reference
model, `event_time = source_time + reviewed_offset`. The offset requires reviewer and
evidence fields; an unaligned asset remains visible but its assertions are excluded from
aligned occurrence counts.

Constant offsets are insufficient for edits, speed changes, inserted advertisements,
montages, reordered segments, and missing portions. The target PiecewiseAlignment stores
source interval, event interval, transform parameters, direction, certainty, evidence,
and reviewer per piece. Gaps remain unmapped. A timestamp found in one upload cannot be
reused on another upload without a supported mapping. The system must not infer original
event date or duration from the upload's filename.

### 06.4 Transcription and timing precision

Use the original audio track when possible. Record channel extraction, resampling,
normalization, voice-activity detection, chunk boundaries, overlap, and language decisions.
ASR returns candidate words, not evidence that recognition is correct. Preserve engine
outputs before cleanup. Transcript correction creates a new revision. Word timestamps
must disclose their alignment source and precision; segment boundaries must not be
presented as exact word boundaries. Unalignable words need an explicit unresolved state.

WhisperX documents word alignment and diarization workflows but also describes limitations
with overlapping speech and some token alignments. It is a technical comparator and an
optional future integration path, not an accuracy guarantee. The reference implementation
supports timed text and standard ASR segment exports, plus an optional faster-whisper
adapter. It has not run downloaded speech models in the delivery environment. See
[WhisperX documentation](https://github.com/m-bain/whisperX) and
[faster-whisper](https://github.com/SYSTRAN/faster-whisper).

### 06.5 Produce two useful viewing ranges

Retain a speech range and a context range. The first highlights the target words; the
second helps a reviewer interpret them. A source-player deep link can be sufficient when
copying media is not permitted. A stored clip needs explicit derivation rights, and its
publication requires a separate right. The target clip manifest includes input/output
hashes, exact requested ranges, observed output duration, tool configuration, rights,
source revision, and any offset introduced by codec behavior.

The v0.1 utility re-encodes instead of treating keyframe stream-copy boundaries as exact.
Its test generates synthetic audio, clips a known interval, and probes the result. This
proves basic local execution and expected duration for that fixture, not frame accuracy
for every codec or variable-frame-rate recording. Output metadata and contextual review
remain release-gate requirements for the full media workflow.


---

## 07. Diarization, speaker identity, and attribution review

### 07.1 Distinct questions require distinct evidence

Voice activity detection asks where speech occurs. Diarization asks which local speaker
label is active at a time. Identification asks which real person, if any, corresponds
to that label. Transcription asks which words were spoken. Active-speaker video analysis
asks whether a visible person is the current speaker. A lower-third may identify a guest
who is not speaking. None of these steps alone answers all of the others.

The initial system uses source speaker labels, introductions, transcript context, reviewed
reference material, and explicit operator inspection. A candidate can stay unresolved.
Diarization labels are scoped to an asset/transcript run, never treated as global person
IDs. `speaker_0` in one episode has no inherent relationship to `speaker_0` in another.
The reference service enforces mapping scope and rejects acceptance through unassigned
labels. See [pyannote's documentation](https://github.com/pyannote/pyannote-audio) for the
distinction between diarization output and external identity resolution.

### 07.2 IdentityEvidence target contract

The target record contains evidence type, source observation or asset, source time range,
local label, candidate person, evidence text or approved derived feature reference,
method/model revision, score meaning, reviewer, decision, and conflict notes. Evidence
types include explicit self-identification, host introduction, official transcript label,
program roster, verified reference-audio comparison, and manual audiovisual inspection.
Evidence independence matters: a transcript label copied from the same faulty caption is
not independent corroboration of that caption.

A machine similarity value is retained as a method-specific score, not displayed as a
universal probability of identity. Thresholds require evaluation on representative panel
audio, telephony, interruptions, low-volume speech, music, aging recordings, and similar
voices. A model that distinguishes speakers well on one clean studio dataset may still
misattribute short overlapping turns. Threshold selection must record false assignments
and abstentions separately rather than optimizing only accepted volume.

### 07.3 Overlap and short turns

The system must support overlapping speech and rapid back-and-forth exchanges. When an
ASR segment spans two speaker labels, assigning every word to the speaker with the longest
intersection is unsafe. The reference helper leaves multi-speaker segments unassigned.
It distinguishes uncertain speaker boundaries from actual overlapping intervals. The
target workflow aligns words to diarization, splits where justified, preserves overlap,
and sends unresolved spans to a reviewer. A clipped audio track with one visible face
is not sufficient grounds to attach an off-camera voice to that face.

Very short utterances such as "yes," laughter, a name, or a fragment may be impossible to
identify independently. They can be linked through context where evidence warrants it,
but acceptance must preserve the basis and uncertainty. Do not fill an identity merely
to avoid an empty cell. An operator must be able to exclude a span from person counts
without deleting the source material.

### 07.4 Human review and corrections

The review interface should show the candidate mapping alongside the audio, surrounding
turns, original transcript, relevant introduction/roster, conflicting hypotheses, and
any reference evidence. Confirm, reject, split, and defer actions create audited events.
An accepted mapping has a named principal in the collaborative target system. The v0.1
single-owner API records reviewer strings and a trusted request actor; those strings are
attestations, not proof that an independent human performed the work.

Changing a mapping invalidates its utterances, occurrences, reviews, and derived display
snapshots. Re-running ASR or diarization does not preserve a mapping automatically if
local labels change. A mapping must reference the precise transcript revision or undergo
explicit revalidation against the new result. This is enforced by revision dependencies
in the reference implementation.

### 07.5 Privacy and minimization

The collection should use only the public communication necessary for the stated
research. Optional voice-reference features are sensitive operational data: keep access
restricted, retention explicit, model/provider transfers separately permitted, and
references tied to the approved purpose. No private-life inference, protected-trait
inference, health interpretation, or personality assessment is part of identity review.
Face recognition is not implemented or required by the core design. Any future biometric
feature needs its own access, legal, security, and evaluation gate instead of inheriting
approval from the text-transcript pipeline.


---

## 08. Exact statements, atomic claims, and proposition matching

### 08.1 Preserve source expression before interpretation

The exact utterance remains immutable within a revision. A claim extractor may normalize
a proposition for search and analysis, but it cannot alter the displayed quotation.
Every candidate claim points to the source utterance revision and a precise evidence
span. The target contract supports several non-overlapping or explicitly related spans
when the source assertion truly spans a turn; it must not splice disconnected words into
a quotation. In v0.1 accepted utterances are contiguous same-label segment selections.

Normalization preserves negation, numbers, units, qualifiers, attribution, modal verbs,
comparators, and temporal references. "There may have been 200" is not "There were 200."
"They claim 200, which is wrong" is not an assertion of 200. "I expect 200 next year" is
a prediction, not an empirical assertion about the current record. Detection of these
features is an extraction problem that requires its own evaluation and human review.

### 08.2 Candidate contract

The target ClaimCandidate records source utterance/revision, text span, normalized
proposition, speech-act classification, checkability kind, extracted scope, unresolved
references, extraction rationale, confidence fields with defined meaning, model/prompt
revision, and suggestions for evidence retrieval. The model cannot set reviewer identity,
approve a claim, supply a fabricated source, merge canonical propositions, or alter
rights/budget state. Output is validated against a schema with unknown fields rejected.

Compound assertions are separated carefully. "The program doubled spending and served
fewer people" normally yields distinct spending and service-volume propositions, each
with its own baseline and period. A causal claim that spending caused fewer people to be
served is a further proposition requiring causal evidence; it must not be added merely
because the sentence contains two correlated observations.

### 08.3 Resolve referents and scope

Resolve pronouns and references such as "that program," "last year," "this bill," and
"the previous administration" from the surrounding source context. Store the supporting
turn/document and a reviewer decision. Relative dates require the event's actual date,
not its upload time. If a date or referent remains uncertain, the scope remains incomplete
and review reuse is blocked. The system can retain multiple candidate interpretations
rather than pick the one that makes a prior fact-check match.

Scope is not a decorative set of tags. It controls compatibility. Preserve entity ID,
metric definition, geographic population, time period, quantity and unit, baseline,
comparison operator, accounting basis, policy/document version, and whether the statement
is absolute, conditional, approximate, or attributed. Financial examples may distinguish
authorization, appropriation, obligation, and expenditure. Statistical examples may
distinguish totals, per-capita values, rates, percentages, and percentage-point changes.

### 08.4 Matching is a two-stage operation

First generate candidates using exact text, normalized text, entities, source links,
lexical retrieval, and optional embeddings. Then apply explicit compatibility checks and
review. Similar wording does not establish a shared proposition. Different years,
geographies, definitions, baselines, negations, and document versions are hard negatives.
The reference `scope_match` is conservative: it reports missing/differing fields and
never authorizes automatic review reuse.

The target equivalence proposal stores both proposition IDs/revisions, shared/different
scope fields, alignment of quantities/units, source context, rationale, and a reviewer.
Accepting equivalence does not destructively delete original IDs. Preserve aliases and
merge lineage. Reversal must restore separate membership and rebuild affected counts.
Canonicalization should be deterministic only after the relevant evidence is reviewed.

### 08.5 Predictions, opinions, and ambiguity

Predictions remain useful records. Store the forecasted event, deadline, condition,
measurement rule, and outcome source when available. Do not evaluate a prediction before
its due date or silently change the criterion afterward. A later outcome assessment is
a separate record, not a retroactive transcript edit. Pure preferences and value judgments
are retained as utterances but should not be forced into empirical findings. Ambiguous
claims require clarification or an explicit unresolved result.

The reference `Proposition.kind` preserves these distinctions but does not implement a
prediction-outcome engine. Full Fact's published workflow is a useful comparator for
claim identification and repetition matching, while not establishing that a general
model can autonomously adjudicate all claims. Reference: [Full Fact AI](https://fullfact.org/ai/).

### 08.6 Extraction evaluation

Measure exact-span grounding, speech-act accuracy, atomicity, scope completeness,
negation preservation, number/unit retention, and abstention. Include quoted denials,
hypotheticals, sarcasm, interruptions, conditional forecasts, vague referents, edited
clips, multilingual material, and ASR errors. A candidate that cites nonexistent words
is an extraction failure even if its normalized proposition happens to be true. Keep
held-out sources and episodes so the evaluation does not reward memorized fixtures.


---

## 09. Evidence research, prior reviews, and recorded findings

### 09.1 Prior fact-checks are research inputs

Google Fact Check Tools, Fact-Check Insights, ClaimReview-bearing publications, and
licensed research feeds can identify related investigations and their source references.
Retain the publisher, original claim wording, publication date, actual review URL,
source appearance references, rating wording, and evidence citations. Do not convert a
publisher's proprietary numerical scale into a universal score. A review found through
several aggregators is one upstream investigation with several discovery paths, not
several independent confirmations.

Google documents claim search and pagination rather than a universal enumerate-all
corpus export. Fact-Check Insights documents bulk JSON/CSV and warns about missing or
inconsistent fields. References: [Google claim search](https://developers.google.com/fact-check/tools/api/reference/rest/v1alpha1/claims/search),
[Fact-Check Insights data guide](https://www.factcheckinsights.org/guide),
[ClaimReview vocabulary](https://schema.org/ClaimReview).

### 09.2 Primary-evidence research

The researcher retrieves the underlying document, dataset, recording, official statement,
measurement, or other appropriate evidence. Each evidence record needs an exact locator,
retained excerpt where allowed, source revision/hash, applicability scope, knowledge date,
and explanation of how it bears on the proposition. A summary written by a model is not
a primary source. A search snippet is generally a lead until the underlying source is
inspected. A cited document can provide context without supporting or conflicting with
the specific assertion.

For numerical claims, preserve the units, numerator, denominator, interval, revision,
methodology, geography, population, and any calculation performed. Calculations should
be reproducible from retained input values and code or formulas. Do not compare a total
with a rate or an authorized amount with an actual expenditure. For quoted claims,
review enough of the original document/recording to establish whether the words carry
the alleged meaning. Source authenticity and evidentiary relevance are separate checks.

### 09.3 Compatible evidence and time

An evidence item may be broader than a claim but must have an explicit applicable scope.
The reference review gate checks direct support/conflict evidence against the proposition's
entity, metric, geography, period, unit, definition, baseline, and comparator. A different
reported quantity may be the substance of a conflict, so quantity is not treated as an
automatic scope mismatch. The reviewer remains responsible for the actual comparison.

Store what information existed at the time of the utterance and what was available at
the time of review when those differ. A later revised dataset can change a present
assessment without establishing what the speaker knew earlier. A contradiction in the
record does not prove intent. A clarification can narrow the interpreted proposition;
it should not erase the original source statement or silently replace the criterion.

### 09.4 Finding semantics

A supported finding means the cited evidence supports the scoped empirical proposition
under the documented interpretation. A contradicted finding means cited evidence conflicts
with that scoped proposition. Mixed means the evaluated compound or qualified proposition
has documented support and conflict that cannot responsibly be collapsed further without
changing its meaning. Prefer atomization where appropriate. Unresolved means available
evidence, identity, scope, or interpretation is insufficient. Not-checkable means the
selected proposition is not presently an empirical question suitable for this workflow.

These are records of a reviewer's assessment, with the review's source and date visible.
They are not attributes of a person's character. A finding must include rationale,
evidence, limits, and reviewer attribution. External review labels remain external even
when similar to internal labels. The v0.1 service enforces some prerequisites; it cannot
verify the soundness of a human argument or independently establish factual truth.

### 09.5 Conflicting evidence and independence

Do not majority-vote documents. Ten articles repeating one press release are not ten
independent measurements. Record common source lineage, methodological disagreement,
revision differences, and whether evidence is primary, secondary, or an external review.
Relevant counterevidence should be retained and addressed, not dropped because it makes
a desired conclusion less convenient. When sources genuinely disagree, the report should
explain the disagreement and what would resolve it. Equal display space is not a substitute
for assessing relevance and methodology.

### 09.6 Review readiness and publication

The target readiness gate checks current dependencies, accepted identity/context,
reviewed extraction, compatible evidence, reproducible calculations where applicable,
correctly attributed prior reviews, disclosed uncertainty, correction status, and rights
for every published excerpt/clip. A completed internal review does not by itself permit
publication. Public output is a separate versioned snapshot with an explicit owner
approval and withdrawal path. The reference release has no public publishing endpoint.
This prevents a draft database write from silently becoming a public accusation.


---

## 10. Counting, duplicate reconciliation, corrections, and snapshots

### 10.1 Units of analysis

An upload is not an appearance; an appearance is not a speaking turn; a speaking turn is
not necessarily a factual assertion; a proposition is not its repeated occurrence; and
an article quoting a statement is not a new time the person spoke. The product must
name every count's unit of analysis. Operational totals include source observations,
assets, original events, confirmed appearances, accepted speaking turns, extracted
propositions, eligible assertion rows, independent assertion occurrences, reviewed
propositions, corrections, and unresolved exclusions.

The reference report deliberately separates eligible assertion rows from distinct aligned
occurrences. Its synthetic example has one original recording, an excerpt copy aligned
to it, and a different original event. Three assertion rows resolve to two occurrences
of one proposition. This is a local demonstration, not a measurement about any real person.

### 10.2 Reference deduplication rule

For an accepted assertion, compute its start and end in a reviewed original-event
timebase. The reference canonical key is the SHA-256 of the event ID, person ID,
proposition ID, event start, and event end. Rows with the same key count as one aligned
occurrence. Source asset IDs and source timestamps remain separately inspectable. Rows
with stale provenance, unreviewed extraction, non-assertion speech acts, or unresolved
alignment are excluded with explicit reasons. A failed row is not deleted from research.

This rule is intentionally conservative and incomplete. Two transcriptions of the same
spoken passage can have slightly different boundaries and therefore receive different
keys. A hash of exact coordinates is not perceptual media deduplication. The UI discloses
that limitation. Do not deploy broad aggregate reporting until reviewed equivalence and
robust event alignment are implemented and evaluated.

### 10.3 Target equivalence model

The target stores explicit occurrence-equivalence proposals with both source occurrences,
their event/asset mappings, supporting alignment evidence, proposition compatibility,
reviewer decision, and merge lineage. Candidate generation may use exact media hashes,
audio fingerprints, transcript alignment, and visual similarity. A candidate similarity
score cannot itself merge occurrences. Near-duplicate quotes in different interviews
must remain separate original speaking occurrences even if the wording is identical.
A repeated replay inside a later program is a redistribution occurrence unless the
person newly asserts the proposition in that later event.

Confirmed equivalence forms a reversible grouping, not destructive record consolidation.
Group membership and representative selection are versioned. One event can contain
multiple original repetitions; identical words at different times are not automatically
one occurrence. Edited montages may cross several original events and require segment-
level mappings. Review correction of an erroneous merge rebuilds affected counts.

### 10.4 Reporting findings without inventing a person score

A claim-level review can be reported with its evidence and state. A corpus report may
summarize which collected and reviewed claim records have each recorded outcome, provided
it states the denominator, selection policy, date window, exclusions, and review version.
It must not translate that distribution into an overall truthfulness percentage,
character judgment, intent conclusion, political ranking, or claim about all speech.

Unreviewed and unresolved items remain visible. Deduplicate repeated claims separately
from repeated assertions when the research question distinguishes them. The v0.1 person
view returns individual completed current reviews and operational corpus counts; it does
not supply an overall honesty or deception score. A future analytical export must carry
its eligibility query and a manifest of member record revisions so a number can be
reproduced rather than trusted as a dashboard label.

### 10.5 Correction lifecycle

Corrections include source transcript fixes, attribution changes, event merges/splits,
new evidence, revised statistics, narrowed claim interpretations, subject clarifications,
and withdrawal of a prior review. A target CorrectionCase records reporter, source,
affected records, category, triage status, reviewer, resolution, and resulting revisions.
A complaint is not automatically accepted, but it is not erased. A verified correction
must trigger an affected-record review before the old public finding is presented as current.

The reference implementation stores reported/verified correction records. Changing a
referenced foundational record triggers transitive invalidation. Automatic appeal handling,
withdrawal, resolution linking, and notification are planned. Merely inserting a correction
record does not run a repair algorithm or change the original claim text. The current
operator must revise the affected record and revalidate its dependents explicitly.

### 10.6 Publication and reproducibility snapshots

The target snapshot includes publication ID/version, cut-off time, investigation scope,
source coverage, eligible record/revision IDs, exclusions, reviewed findings, media/excerpt
rights, redactions, code/query version, and signature/checksum. A snapshot is immutable;
a correction publishes a new version with a change explanation. A revoked asset cannot
continue to be publicly served simply because a prior snapshot referenced it. Retain a
permitted tombstone or explanation instead. Public publication is not part of v0.1.


---

## 11. Architecture, storage, and component boundaries

### 11.1 Reference deployment

The shipped system is a modular Python application with a FastAPI operator API, a CLI,
static browser assets, a SQLite revision ledger, optional raw local files, and a durable
job-ledger library. No database server, vector database, message broker, external model,
cloud account, or private application is necessary for the synthetic demo. The source
registry is packaged data. JSON Schemas are generated from Pydantic models. The browser
uses the same authenticated API as command-line clients.

The current component ownership is explicit:

| Module | Responsibility |
|---|---|
| `models.py` | Typed canonical record payloads and local field invariants |
| `service.py` | Cross-record validation, rights/currentness checks, ledger projection |
| `store.py` | Transactional revision storage, heads, dependencies, audit/outbox |
| `connectors/registry.py` | Source inventory and implementation/access status |
| `connectors/parsers.py` | Native source records to observation candidates |
| `connectors/http.py` | Bounded source metadata/search clients |
| `ingest.py` | Retained file archive and revision-aware import receipts |
| `transcripts.py` | Timed text and ASR-export normalization |
| `speech.py` | Optional local ASR/diarization calls and conservative label matching |
| `media.py` | Local clip-range planning and FFmpeg derivation |
| `jobs.py` | Standalone queue records, leases, attempts, and safe completion |
| `api.py` / `cli.py` | Operator entry points; neither is a truth engine |

### 11.2 Canonical source of truth

Record revisions are canonical. Current heads point to a revision and may be stale.
The dependency index records which parent revisions justified a child. Changes to a
parent mark its descendants stale. Audit and outbox entries are committed with the
record revision. Indexes, search embeddings, UI summaries, and analytical groupings
are derived views and must be rebuildable. A model-provider cache cannot become a
second authoritative claim store.

SQLite uses a single-workspace reference schema. The API creates a separate store
connection per request, while write operations use immediate transactions. The code
is not a multi-tenant high-throughput system. A PostgreSQL adapter is planned before
multi-user production use. It must preserve revision identities and dependency semantics;
changing the storage engine must not change the meaning of a claim or count.

### 11.3 Target services and independent scaling

The target architecture has an operator API/UI, discovery planner, source workers,
acquisition workers, isolated media workers, extraction/retrieval workers, review service,
projection service, and retention/publication workers. Initially these may be modules in
one deployable application with explicit process separation for untrusted media. Split
services only when workload or security requirements justify the operational cost.

Metadata discovery is network-bound; audio processing may be CPU/GPU-bound; raw media
storage is capacity-bound; human review is a separate bottleneck. A queue must distinguish
these resource classes. Running an audio job in an HTTP request is not acceptable for the
target deployment. Each worker consumes a versioned input envelope and produces a
versioned result that references its exact inputs. Failures preserve diagnostic states
without marking the underlying claim false or the investigation complete.

### 11.4 Production database design

The PostgreSQL design retains append-only record revisions, current heads, dependency
edges, audit events, and outbox events. Add workspace IDs, principal IDs, row-level access
controls, immutable source artifact manifests, durable task attempts, and explicit
publication snapshots. Typed projection tables accelerate common queries over events,
persons, turns, proposition scopes, occurrence groups, and review states. A projection
has a generation/version and can be rebuilt from canonical revisions.

Database constraints must enforce nonnegative and ordered intervals, referential
integrity, unique source-native keys, expected revision checks, and group membership
integrity. Transactional application validation remains necessary for rich scope/identity
rules; SQL alone does not determine semantic equivalence. Cross-workspace joins are
prohibited unless an explicit shared-source abstraction has reviewed permissions.
Multi-tenancy must be tested using adversarial foreign IDs at every API boundary.

### 11.5 Search and graph capabilities

A minimal local search can use lexical indexes and explicit filters. Semantic retrieval
is an optional candidate-generation port. A graph representation can connect source,
event, asset, utterance, person, proposition, evidence, and review objects, but must not
replace the canonical revision store or bypass source access. Graph expansion returns
provenance paths and supported relations, not unsupported causal assertions. An external
index response must include canonical IDs and source revisions that the ledger can check.

The default standalone build does not connect to any external retrieval service. A
future adapter must conform to the generic retrieval contract and be removable. No
private repository code, namespace, or credentials are embedded in the architecture.

### 11.6 Migration and rollback

Schema changes need explicit migration IDs, a backup before execution, a forward
migration test, compatibility checks against generated contracts, and a rollback or
restore plan. Do not silently regenerate IDs when migrating record kinds. A rollback
must disable new publication/processing first, preserve pending jobs and source receipts,
and avoid acknowledging outbox events whose effects are not durable. A code rollback
that makes new records unreadable is not sufficient; define a data compatibility window
or a validated restore procedure.


---

## 12. API, commands, event contracts, and concurrency

### 12.1 Implemented operator API

The reference API requires a bearer token for all data, schema, plan, and integrity
endpoints. The static shell and minimal health response are public within the local
server. The token is injected from `SL_API_TOKEN`, must be at least 32 characters, and
maps to the single-owner actor. Reviewer text in a record is separate from the request
actor. The server does not offer a public account-registration flow.

| Method and path | Implemented behavior |
|---|---|
| `GET /healthz` | Service/version/mode only |
| `GET /api/sources` | Packaged connector registry |
| `GET /api/counts` | Record totals by kind, not person assessments |
| `GET /api/schema/{kind}` | Generated record payload schema |
| `GET /api/records/{kind}` | Bounded record list with offset/limit |
| `GET /api/records/{kind}/{id}` | Current or explicitly requested historical revision |
| `GET /api/history/{kind}/{id}` | Revision history |
| `POST /api/records/{kind}` | Validated append/update with expected revision |
| `GET /api/people/{id}/ledger` | Eligible assertions, evidence/reviews, exclusions, coverage |
| `POST /api/discovery/plan` | Non-executing source plan |
| `POST /api/scope/compare` | Candidate compatibility; never automatic review reuse |
| `POST /api/clips/plan` | Bounded source/context intervals; no media download |
| `GET /api/integrity` | Audit and record-hash consistency checks |
| `GET /api/openapi.json` | Authenticated OpenAPI contract |

A record write body contains `record` and `expected_revision`. Creating a new record
uses expected revision zero. Updating requires the current head revision. A conflict
returns HTTP 409. Missing references return 404 and invalid payloads/invariants return
422. Oversized write requests exceed a 4 MiB bound and return 413. The code stores a
trusted request actor rather than accepting an arbitrary actor header.

### 12.2 Idempotence versus concurrency

An exact retry with the correct expected revision may return the existing record without
creating another revision. A stale expected revision is still a conflict, even if the
request resembles an old payload. Do not let generic upsert semantics overwrite a newer
review. Imports use stable source IDs and compare normalized content so unchanged
source records do not create repeated revisions merely because retrieval time changed.
A changed source payload creates a new revision using the current expected head.

Stable observation IDs are source-scoped; IDs do not prove two sources refer to the same
underlying investigation. Canonical linking requires an explicit relation or reviewed
equivalence. Cross-source raw record collisions must not overwrite material. Content
hashes and source-native IDs both need to be retained because neither alone answers all
deduplication questions.

### 12.3 CLI as the reference workflow surface

The CLI supports source listing, deterministic planning, name-only subject seeding,
synthetic demo seeding, record get/put, person-ledger projection, file ingestion, timed-text
or ASR-export import, explicit paginated source discovery, local clip derivation, optional
speech processing, integrity checks, native SQLite backup, private JSON export, and schema
export. Commands that require paid or authenticated providers do not run automatically.
Source credentials are environment configuration, not model arguments or repository files.

The CLI's `discover` command writes raw responses and a pagination receipt; it does not
promote results to appearances. `ingest` requires an explicit source and rights grant.
`import-transcript` requires a known asset. Local media commands verify the registered
asset checksum before processing. This sequence makes permission and lineage visible
instead of hiding several unrelated operations behind one ambiguous "analyze person" call.

### 12.4 Target task and event envelopes

The production task envelope contains task ID, investigation ID/revision, source/operation,
input record IDs/revisions, idempotency key, cursor, budget reservation, rights snapshot,
worker class, attempt, lease token/expiry, deadline, and output schema version. A result
contains outputs, next cursor, bytes/time/tokens used, completion meaning, errors, and
source receipts. Secret values never appear in either envelope.

The reference store emits `record.created` and `record.revised` outbox entries in the
same transaction as the record. Target event types add discovery.page_received,
asset.acquired, transcript.produced, attribution.reviewed, utterance.accepted,
claim.proposed, evidence.revised, review.completed, dependencies.invalidated,
correction.opened/resolved, publication.withdrawn, and retention.completed. Consumers
must be idempotent and track processed event IDs; an outbox row is not proof a downstream
effect occurred. Outbox consumption and delivery acknowledgements are not implemented
in v0.1.

### 12.5 Compatibility and contract testing

Generated JSON Schemas and OpenAPI snapshots are version-controlled. CI regenerates them
and fails on unexplained drift. New record fields require migration/backward-compatibility
review. Unknown fields are rejected rather than silently ignored. Provider adapters have
recorded source fixtures and explicit parser versions. A commercial vendor contract must
be based on an actual supplied schema, not an invented endpoint that happens to look
plausible. Contract tests prove known shapes, not provider access or real-world accuracy.


---

## 13. Operator experience and target interface

### 13.1 Shipped interface

The v0.1 browser interface provides token entry, people, source registry, a non-executing
discovery planner, a raw record inspector, integrity checks, and a person-ledger view.
The ledger shows exact words, source and event coordinates, source references, current
completed reviews, provenance IDs, coverage, exclusions, and operational count units.
Synthetic examples are visibly marked. The token stays in page memory and is removed
from the input after connecting; no browser persistent storage is used.

The UI uses text-node construction rather than interpreting source text as HTML. External
links allow only HTTP/HTTPS and use safe relationship attributes. A restrictive content
security policy, no-store response headers, and no third-party scripts reduce avoidable
exposure. This is not a full transcript annotation editor, collaborative review tool,
or public reporting site. Those interfaces are designed below and remain planned.

### 13.2 Investigation home

The target home shows the research question, subject identity, date/window basis, source
coverage matrix, blocked access, queue state, accepted versus unresolved material, budget
consumption, and recent provenance changes. It must not open with a reputation score.
The primary action is to resolve the next missing piece of evidence or coverage.
Missing source access is shown separately from an empty search. Selected filters are
preserved in exported reports so the user can reproduce the displayed subset.

Each coverage tile should open the underlying query plan, receipts, cursor history,
results, and exclusions. A stopped run must show whether it reached its budget, exhausted
the particular query, failed, or was manually paused. No "100% complete" meter is shown
without a documented closed inventory and an appropriate denominator.

### 13.3 Appearance workbench

The appearance page groups original event candidates and associated assets. It displays
event time with precision/evidence, upload dates separately, source provenance, candidate
participants, access rights, and an asset comparison panel. The operator can mark mentioned-
only, confirm appearance with evidence, split a montage, or leave the event unresolved.
Potential duplicates are suggestions; the UI requires a reviewed alignment or equivalence
decision before count grouping changes.

The asset panel shows available tracks, probe data, checksum, source-player link, local
playback where permitted, transcript revisions, and processing attempts. An inaccessible
recording still has a useful metadata view. Source-player links are a first-class outcome,
not treated as a failed substitute for downloaded media.

### 13.4 Transcript and speaker review

A synchronized transcript view shows waveform, source video when allowed, local speaker
labels, word/segment timing precision, overlap, current mapping decisions, and surrounding
turns. Selecting a turn should show why the identity was proposed and which introduction,
roster, or reviewed evidence supports it. The operator can split segments, edit transcript
text as a new revision, correct a mapping, mark uncertain audio, and accept a contextualized
utterance. Keyboard navigation and readable uncertainty labels are important for review
throughput. Color is not the sole carrier of status.

The claim extractor's suggestions appear next to the exact source text, with span
highlighting and explicit speech-act labels. The interface makes it easy to reject a
claim that is merely quoted, hypothetical, or incomplete. Scope fields include unknown
states rather than forcing guessed values. The system should warn when a proposed
normalization drops a negation, numeral, qualification, or attribution.

### 13.5 Evidence and review workspace

The claim page presents the scoped proposition, all related original occurrences,
source context, matching proposals, external reviews with publisher attribution, primary
evidence, calculations, counterevidence, and limitations. Candidate evidence is not marked
supporting until that relationship is reviewed. The user can inspect exact source locators
rather than only an AI summary. Conflicting reviews remain visible instead of selecting
the most convenient one automatically.

Completion has explicit checklist items for identity, context, assertion, scope, evidence,
currentness, and access. A separate publication preview shows which excerpts/clips are
permitted and which record revisions will be frozen. The product must not make a draft
review look publicly finalized because a form has a green save button.

### 13.6 Corrections, history, and accessibility

Every material revision exposes a readable diff and affected descendants. A stale badge
explains the actual changed parent. Correction cases show the report, source, decision,
resolution, and changed public snapshots. Report exports include date, scope, coverage,
limitations, exact sources, and corrections. Accessibility targets include keyboard-only
operation, visible focus, readable contrast, labels for uncertainty, caption access,
no forced autoplay, and alternatives to waveform-only interactions. These need browser
and accessibility evaluation, not a claim based only on HTML structure.


---

## 14. Model orchestration, tool boundaries, and prompts

### 14.1 Provider-neutral roles

Use models only where they have a defined role: speech recognition, local diarization,
quote-to-window retrieval, claim candidate extraction, scope interpretation, evidence
search planning, source comparison, or draft explanation. Each role has a typed input,
output, model/prompt/configuration version, budget, provenance policy, and evaluation set.
The core runs without any generative-model credentials. The reference code does not
implement an automatic fact-adjudication model or silently fall back to one.

A small or inexpensive model may classify candidate tasks; a more capable model may
analyze difficult evidence. The design does not assume a particular vendor, current
model name, rate limit, or token price. Capability profiles and prices are runtime
configuration that must be checked against provider documentation when adopted. A
provider's marketed benchmark does not establish performance on panel-discussion audio
or the project's own claim-review corpus.

### 14.2 Context packs

An extraction context pack contains the exact utterance and nearby turns, source timebase,
reviewed identity status, event-date evidence, transcript revision, and allowed source
metadata. An evidence-analysis pack contains the scoped proposition, asserted occurrence,
primary evidence excerpts/locators, relevant prior-review provenance, uncertainty, and
known counterevidence. Do not include unrelated personal information or political
preferences. Do not use the speaker's ideology, party, or network as a feature of factual
correctness. Speaker identity needed for attribution is separate from claim evidence.

Context packs identify missing information explicitly. A model cannot fill a blank source
locator, invent a document, or turn an inferred date into a source fact. The returned
claim/evidence proposals must cite existing provided record IDs and spans. An output
validator rejects references not present in the permitted input or tool results.

### 14.3 Prompt and output rules

The extraction prompt asks for candidate propositions and speech acts, not a verdict.
The evidence prompt asks for a comparison under explicit scope, missing information,
and a list of source-grounded reasons. It must distinguish an external publisher's
assessment from a proposed internal assessment. The publication draft prompt may describe
only an already reviewed finding and its current citations; it cannot create a new
finding by writing persuasive prose.

All source text is untrusted data. Instructions found in a transcript, article, caption,
HTML comment, or document must not override the tool policy, change source scope, reveal
credentials, trigger external writes, or tell the system how to classify a person.
Source content is delimited and tools are provided through fixed, least-privilege
interfaces. Prompt injection defense is also enforced outside prompts: allowlisted
operations, bounded retrieval, schema validation, and explicit write approvals.

### 14.4 Caching and reproducibility

Cache by task type, exact input hashes/revisions, model version, prompt version, generation
settings, parsing version, and rights partition. Do not reuse a model result after its
underlying transcript, person mapping, evidence, or scope changes. Store the raw output,
validated output, rejection reason, retry count, usage, and tool trace where permitted.
A failed or unparsable model response becomes a failed proposal, not a positive result
from a fallback heuristic that hides the loss of evidence.

The operator can compare model proposals across versions on a held-out corpus. A model
upgrade requires regression testing on identity errors, negation, scope hard negatives,
source hallucinations, and correction propagation. Disagreement among models is not a
vote that establishes truth. A deterministic arithmetic or unit-conversion check should
be implemented as code rather than delegated to repeated free-form model judgments.

### 14.5 Optional speech adapters in this release

`speech.py` includes an optional faster-whisper call, a pyannote diarization call, and a
conservative segment-to-label overlap matcher. These use approved local files and rights
grants. They do not download source videos or assign a real person name. Model weights,
GPU runtimes, gated model permissions, and large optional dependencies are not bundled.
The test suite exercises adapter logic with fakes; actual model inference requires a
separate integration run with logged versions, input rights, and human-labeled evaluation.

The target isolated worker should record content hash, preprocessing, model weights
revision, dependency lock, hardware, timestamps, and any context retained across chunks.
Do not label a mocked adapter test as a successful speech-recognition benchmark.


---

## 15. Security, privacy, and deployment constraints

### 15.1 Threat model

Untrusted inputs include source URLs, API responses, compressed corpora, HTML/transcripts,
media containers, external review text, model output, signed source links, and uploaded
configuration. Threats include server-side request forgery, local-file access, malicious
media decoders, decompression exhaustion, cross-site scripting, prompt injection,
credential leakage, cross-workspace access, forged identity mappings, source poisoning,
duplicate inflation, race conditions, and stale or unauthorized publication.

The project also treats evidentiary errors as integrity failures. A valid login does not
make a statement attribution correct. A checksum does not make a quote authentic.
Security controls, provenance checks, and factual review are complementary, not
interchangeable.

### 15.2 Reference security posture

The reference API is intended for a private local single-owner workspace. All data routes
require a bearer token. HTTP write bodies are bounded; source clients cap responses,
reject redirects, use fixed endpoints, and suppress credential-bearing error details.
The browser renders untrusted content as text and does not persist the token. Media
utilities use an explicit local root, fixed command arguments, and no shell interpolation.
SQLite queries use parameter binding. External source links are not automatically fetched.

The Docker configuration uses a non-root process, loopback-bound host port, read-only
application filesystem, a dedicated data volume, dropped capabilities, and no-new-
privileges. It does not claim a production security audit, multi-tenant isolation, rate
limiting, TLS termination, centralized secret storage, full decoder sandboxing, or a
complete public-service defense. Docker execution itself must be validated on the target
host. No public deployment is authorized by passing the unit tests.

### 15.3 Production identity and authorization

The target system uses actual authenticated principals and server-side roles for owner,
source operator, researcher, reviewer, publisher, and read-only auditor. Roles constrain
operations and source access. Workspace IDs come from authenticated scope, never from an
unchecked client filter. Every endpoint, export, object-store link, search query, and
background job is bound to the authorized workspace and source grants. Audit actor IDs
are server-controlled. The client cannot approve its own role by setting reviewer text.

Database row-level controls and application authorization are tested independently.
Foreign record IDs, stale sessions, object-store keys, job IDs, and cached search results
must not leak data across workspaces. The target deployment should support separate
physical workspaces where rights or customer isolation make that simpler than shared
multi-tenancy. No other project's identity provider or tenant table is assumed.

### 15.4 Network and media isolation

A future general source fetcher needs hostname/scheme allowlists, DNS/IP validation,
redirect revalidation, private-network and metadata-service denial, response/time limits,
and controlled egress. Signed URLs and authentication query parameters must not appear
in model contexts or public logs. The source URL retained for provenance may need a
redacted public variant and a restricted acquisition reference.

Media workers should not have database-owner credentials or unrestricted outbound
networking. A job receives a validated local object and outputs a derivative plus a
manifest. Resource limits cover memory, CPU/GPU, wall time, disk, subprocess count, and
output expansion. Source media is read-only. Malformed decoders fail the job, preserve
a safe error code, and do not terminate the queue or reinterpret missing words.

### 15.5 Retention and privacy

Retain only what the collection purpose and source agreement allow. Rights include
provider transfer and indexing, not just downloading. Credentials live outside Git and
outside source manifests. Biometric reference features, when separately approved, are
restricted and minimized. Do not collect private communications or infer protected or
sensitive personal attributes as part of public-statement analysis. Removal requests,
source access changes, and verified attribution errors require auditable handling.

The reference implementation checks grant expiry for new dependent work and currentness,
but it does not automatically purge raw files. A retention worker, deletion proof,
publication withdrawal, backup retention policy, and testable restore implications are
mandatory before restricted real-world collections are used in production.

### 15.6 Supply chain and release checks

Keep direct dependencies explicit and record the tested runtime. Generate an environment
manifest and a resolved dependency lock in a network-enabled environment; do not fabricate
a hash lock when dependency resolution failed. Optional GPU/model dependencies belong
in separate worker images with recorded license/model access and pinned revisions.
CI must check tests, generated contracts, namespace independence, dependency audit,
secrets, and relevant source/model integration gates. Unit tests are necessary but do
not replace live permission checks, deployment inspection, or an adversarial review.


---

## 16. Evaluation, acceptance criteria, and release gates

### 16.1 Evidence levels

Separate schema/unit proof, source-shaped fixture proof, mocked protocol proof, live API
proof, authorized media proof, human-labeled model evaluation, deployment proof, and
production observation. The validation report must identify which level supports each
claim. Passing a parser fixture does not prove source coverage. Passing a mocked speech
adapter does not prove transcription accuracy. Passing the synthetic duplicate example
does not establish robust deduplication across edited broadcasts.

All evaluation fixtures must be synthetic or explicitly permitted. Real-person labels
and findings require traceable source evidence. Do not fabricate a benchmark about a
named subject to make the repository appear complete. Hold out programs, time periods,
channels, and recording conditions from development where possible.

### 16.2 Required test categories

Contract tests cover record shapes, unknown fields, timezone/interval validity, expected
revisions, source parser mappings, source date semantics, pagination, repeated cursors,
response limits, credentials, and schema drift. Provenance tests cover missing/stale
parents, cycles, identity corrections, transcript revisions, rights expiry, evidence
scope, and audit consistency. Counting tests cover original/copy/replay distinctions,
repetition across different events, uncertain offsets, scope differences, and exclusions.
Security tests cover authentication, XSS-safe rendering, oversized requests, media path
boundaries, cross-workspace IDs in the target deployment, and restricted-source exports.

Media evaluation measures transcription error, word/segment timing error, diarization
error, speaker mapping errors, overlap handling, and performance by source condition.
Claim extraction evaluation measures grounding, speech act, atomicity, number/negation
preservation, scope completion, and abstention. Evidence review evaluation uses a
reviewer-authored rubric for applicability, cited-source correctness, handling of
counterevidence, and correction responsiveness. Human disagreement is recorded and
adjudicated, not hidden by collapsing to one unexplained label.

### 16.3 Proposed quality targets are not measured claims

For an initial reviewed pilot, require zero known wrong-person attributions among released
accepted turns and zero unsupported exact-quote spans. This is a release-blocking review
criterion, not a statistical guarantee about unreviewed material. Choose quantitative
model targets only after a representative baseline. Report numerators, denominators,
confidence intervals, source strata, and abstentions. A small clean sample cannot support
claims of near-perfect accuracy on all broadcasts.

The prototype's exact-coordinate deduplication must pass original/copy fixtures, while
edited/offset-drift cases remain explicitly unsupported until the alignment milestone.
For production counting, a curated hard-negative set must include the same words spoken
on different dates, a host quoting a guest, a montage, a replay, and two differently
bounded transcripts of the same utterance. No source-induced duplicate inflation is
acceptable in the released reviewed corpus.

### 16.4 Release gates

| Gate | Required evidence | Current meaning |
|---|---|---|
| G0: independent specification | Standalone contracts, source map, no external project dependency | Design and namespace guard |
| G1: local reference slice | Clean unit/API tests, synthetic demo, revision invalidation, clip utility proof | Shipped local proof |
| G2: real source contract | Authorized sample from each activated source; schema/permission receipt | Per-source access gate |
| G3: one-person private pilot | Permitted original/copy pair, reviewed speaker/context, sourced claims | Not yet completed |
| G4: robust media/occurrence linkage | Piecewise alignment, reversible equivalence, hard-negative tests | Planned |
| G5: assisted review workflow | Evaluated model proposals, reviewer UI, correction resolution | Planned |
| G6: production operations | Auth/RBAC, storage migration, isolated workers, budgets, retention, restore/load tests | Planned |
| G7: publication | Rights-complete snapshots, editorial approval, corrections/withdrawal | Planned; disabled |

The gates are cumulative for the relevant deployment. A source-specific feature may pass
its own G2 while another source remains blocked. No requirement says every commercial
provider must be purchased before useful private research; manual and open inputs can
prove the workflow. However, the product must not advertise an unactivated source as live.

### 16.5 Regression and reporting

Every bug fix adds a test that would have detected the error. Do not weaken correctness
gates to increase accepted volume. Re-run schema and openAPI generation after model or
route changes. Re-run the deterministic demo after every data-model change. Record the
Python/platform versions, dependency snapshot, commands, test results, optional skips,
source access, and current limitations. Maintain a machine-readable feature/status
manifest so a coding agent cannot infer completion from a document title or TODO stub.

The initial local validation report includes the executed synthetic tests and FFmpeg
clip test. Live source fetches and dependency locking encountered DNS failures in the
build environment. Provider credentials, speech model weights, Docker deployment, and
remote repository creation were not supplied or completed. These are explicit gates,
not silent assumptions hidden behind green unit tests.


---

## 17. Capacity planning, costs, and operating budgets

### 17.1 Workload variables

Define `A` as original audio/video hours acquired, `D` as distinct hours after asset
reconciliation, `P` as processed hours, `T` as accepted target-speaker hours, `U` as exact
utterances, `C` as candidate claims, and `R` as reviewed propositions. Keep these separate:
a mirrored clip can increase acquired bytes without increasing original hours or claims.
A failed diarization pass can increase compute without increasing accepted turns.
Operational reports need both useful output and failed/repeated work.

Metadata work is measured in requests, pages, results, and bytes per source. Source costs
may depend on request, mention, transcript, recording hour, historical backfill, seat,
or contract. Do not hard-code a universal quota or monthly price from an old overview.
Each activated source gets a current configured cost model and an explicit budget.

### 17.2 Storage estimates as formulas

For constant media bitrate `b` megabits per second, decimal storage per hour is
`b × 3600 / 8 / 1000` gigabytes, or `0.45 × b` GB/hour. Thus an illustrative 2 Mb/s copy
occupies about 0.9 GB per hour before container, metadata, replicas, and filesystem
overhead. This is an arithmetic example, not a measured source bitrate. Audio at 64 kb/s
is approximately 28.8 MB/hour. Actual sources must be probed and measured.

Storage planning includes originals, derived audio, retained context clips, transcripts,
raw source files, indexes, revision history, backups, and temporary worker output.
Set retention separately per asset class. A duplicate media hash may permit deduplicated
storage within an allowed rights boundary, but do not collapse distinct source metadata
or assume two customer licenses allow shared retained objects.

### 17.3 Compute and model usage

Let `f_asr` be measured compute-seconds per audio-second for a chosen model/hardware/config.
ASR compute hours are approximately `P × f_asr`, before retries and preprocessing.
Diarization, alignment, and video analysis need their own factors. A publisher's reported
speedup is not a planning guarantee. Benchmark representative recordings, including long
panels and overlap, and reserve headroom for failures and reprocessing after corrections.

For a generative-model stage, cost is `input_tokens × input_unit_price + output_tokens ×
output_unit_price`, plus any tool or hosting charges. Cache reuse reduces calls only when
all relevant input/model/rights revisions match. Count rejected or malformed responses as
costs, not as zero-cost successful reasoning. A cheap routing model can reduce expensive
analysis only if its missed-candidate rate is acceptable on the evaluation corpus.

### 17.4 Human-review capacity

Human review is often the pacing constraint. Measure minutes to resolve an appearance,
map a speaker, accept a contextualized utterance, review a claim, and resolve a correction.
Separate straightforward confirmations from difficult cases. The interface should reduce
repetitive work by presenting source context and prior compatible research, not by
encouraging acceptance without evidence. Review throughput is a measured operational
quantity, not a reason to weaken the inclusion rules.

### 17.5 Budget enforcement

The target budget ledger reserves spend or units before dispatch and reconciles actual
usage after completion. It has separate caps for source requests, acquired bytes, media
hours, model tokens, worker time, and review workload. A task that exceeds its budget
pauses with a saved cursor/result receipt. It does not silently drop material and mark
the run complete. A retry shares a logical task budget but records each physical attempt.
Reconciliation releases unused reservations and handles crash recovery explicitly.

The reference CLI offers page and record limits but does not implement a financial budget
reservation service. Large paid crawls are therefore not enabled. Begin with a bounded
authorized pilot, measure actual resource usage, then set the capacity and cost envelope.


---

## 18. Implementation sequence and work-package acceptance

### 18.1 Delivery philosophy

Build one reliable chain before broadening scale: a source observation becomes an event,
a permitted asset, a transcript, a reviewed speaker mapping, an exact utterance, a scoped
claim, evidence, and an inspectable review. Preserve every source as an input option but
do not simulate vendor integration. Each milestone closes a testable vertical step.
A feature is complete only when its user-visible path, data contracts, error states,
provenance, and relevant tests are complete together.

### 18.2 Milestone A — reference foundation

This milestone establishes the independent namespace, source registry, typed records,
revision store, structural gates, CLI/API, synthetic demo, basic operator UI, local clip
utility, source-shaped parsers, fixed-origin clients, and test suite. The current release
covers this reference slice. It does not include automatic data collection for a real
subject, general LLM extraction, or production deployment. Record the local proof and
remaining limitations precisely.

### 18.3 Milestone B — authorized source onboarding

For each selected source, obtain an actual permitted sample and record its access scope.
Exercise the client/parser against it. Capture source-native field names, pagination,
empty responses, errors, date semantics, identifiers, updates, and download constraints.
Register raw-file/response manifests and parser replay. Implement any missing transport
only from the verified contract. A manual export can satisfy a private pilot without
pretending the provider has an unattended API integration.

Acceptance requires a source worksheet, rights basis, real sample manifest (not necessarily
redistributed in Git), tested parser fixtures with permitted/synthetic equivalents,
bounded failure behavior, and an honest coverage record. A provider marketing page alone
does not satisfy this milestone.

### 18.4 Milestone C — one-person private pilot

Use the named subject configuration with a user-approved date/source window. Locate one
original appearance and a copied excerpt through at least two independent discovery paths.
Acquire the material through permitted channels, record hashes and source dates, process
sufficient context, and have a reviewer resolve speaker labels. Extract several claims
without changing the source words. Record at least one unresolved claim if evidence is
insufficient; the pilot is not required to produce an adverse finding.

Acceptance requires original/copy reconciliation, demonstrably correct identity/context,
exact source-linked utterances, claim scope, cited evidence, correction capability,
coverage exclusions, and a reproducible private report. No fabricated real-person result
may be used to satisfy the gate. Source and model integration failures are retained and
reported rather than bypassed.

### 18.5 Milestone D — robust media and assisted review

Implement piecewise media alignment, reversible occurrence-equivalence groups, true
word/turn review, context bundles, actual identity-evidence records, model proposal ports,
source-grounded extraction, optional retrieval, and the reviewer workspace. Evaluate
against a held-out corpus containing multi-speaker interruptions, difficult audio,
montages, repeats, misleading edits, and scope hard negatives. Integrate correction cases
and avoid silently carrying findings across changed evidence.

### 18.6 Milestone E — operational and public readiness

Add production storage, actual roles/workspaces, isolated media workers, durable plan
execution, budget reservation, source retention rules, provider/model version management,
monitoring, restore tests, load tests, and incident response. Only afterward enable
public snapshots with an explicit editorial/rights gate, stable citations, correction
notices, and withdrawal. Collaborative and public deployments have different risk than
a local research tool; their readiness cannot be inferred from a successful demo.

### 18.7 Ticket contracts

The ticket index contains independent `SL-` work items. Each ticket specifies dependencies,
implementation status, scope, expected files/components, acceptance criteria, negative
tests, and evidence needed to close it. Source-specific tickets do not claim all sources
are implemented. A coding agent must update the status manifest after executing tests
and explain what remains access-dependent. The next milestone is chosen by the smallest
unmet gate, not by the most visually impressive feature.


---

## 19. First real investigation: acceptance scenario

### 19.1 Subject and scope

The included example subject is Scott Jennings because the project discussion used that
name. This specification does not supply claims about his current role, channels,
statements, or record. Start by reviewing identity references and defining an explicit
public-source/date window. A name-only configuration is sufficient to generate a plan,
not to confirm an identity in a video. Use a new research database rather than the
synthetic demo database.

The first investigator should approve a small set of available sources and no more
than the agreed request/media budget. Name searches, a program inventory, and a quotation
lead can be run separately and compared. The objective is to prove the evidence chain,
not to collect a predetermined number of inaccurate statements or force an adverse result.

### 19.2 Required evidence bundle

The pilot bundle contains its investigation configuration, identity references, source
queries and receipts, access/rights records, raw observations, event and asset decisions,
source and event date evidence, byte hashes for acquired local media, transcript/model
outputs, speaker-mapping rationale, selected utterances with context, claim extraction,
evidence sources, review record or unresolved state, and coverage/exclusion report.
Licensed material is kept privately; Git contains code, contracts, synthetic fixtures,
and permitted manifest metadata only.

The bundle should contain an original recording and a copy/excerpt of the same passage,
plus a distinct event when available. Demonstrate that the copy is grouped with the
original while a newly spoken repetition remains distinct. If alignment cannot be
established, preserve the uncertainty and exclude that row from aligned occurrence
counts. A smaller verified bundle is preferable to a larger ambiguous claim of completion.

### 19.3 Acceptance checks

A reviewer can open each accepted utterance, hear or inspect the source, identify the
speaker on documented grounds, read the surrounding question and qualification, and
verify that the exact words were not invented or spliced. The event date is supported
or explicitly unknown. Source timestamps seek the right location for the referenced
asset. Scope interpretations and evidence locators are inspectable. Any internal finding
has a human-authored review rationale and no unsupported inference of intent.

The report declares which sources were not searched, what access failed, which episodes
were inaccessible, which turns were ambiguous, and which claims remain unreviewed.
An upstream correction is introduced deliberately into a copied test workspace and
verified to stale the affected downstream results. A backup is restored in a separate
location and its integrity checks are rerun. These are release evidence, not promises.

### 19.4 What the delivered repository does not pre-fill

It does not identify actual YouTube channel IDs for the subject, fetch his entire media
history, download his videos, assign his voice to diarization labels, produce a factual
finding about him, or grant access to commercial archives. The repository provides the
mechanisms, examples, and specification for doing that work with actual authorized
sources. The optional speech adapters still need model/hardware validation. The real
pilot is therefore a distinct next gate rather than a claim hidden inside the demo.


---

## 20. Hard cases and required behavior

| Case | Required behavior | Failure to prevent |
|---|---|---|
| Subject's name only in title | Candidate appearance; inspect actual program | Treating all audio as the named person's speech |
| Host discusses subject | Mention-only unless presence is established | Inventing an appearance |
| Subject quotes another person | Preserve quotation speech act and context | Counting quoted content as the subject's assertion |
| Host rejects a false proposition | Record rejection, not assertion | Reversing the meaning through keyword matching |
| Short interjection | Defer identity unless evidence supports it | Assigning every "yes" to the most visible face |
| Two voices overlap | Preserve overlap and uncertainty | Attributing mixed words to one person |
| Sequential speakers in one ASR segment | Split/review or leave unassigned | Majority-duration assignment of all words |
| Lower-third names a guest | Identity lead only | Assuming the named guest is the current speaker |
| Caption error changes a number | Review audio and revise transcript | Treating ASR/caption output as unquestionable |
| Old interview newly uploaded | Separate event and upload clocks | Moving a historical claim into the present |
| Same clip on twenty channels | One original occurrence with copies | Multiplying the speech count by repost count |
| Same words in three interviews | Distinct event occurrences | Collapsing real repetition through text equality |
| Montage from several events | Segment-level event mappings | One false original-event assignment |
| Edited advertisement inserted | Piecewise alignment or unresolved gap | Reusing a constant timestamp offset incorrectly |
| Changed playback speed | Reviewed time transform | Claiming source seconds equal event seconds |
| Cropped statement omits qualification | Acquire context or mark insufficient | Publishing a misleading fragment |
| Generic archive date | Preserve raw date until interpreted | Calling it the recording date automatically |
| Quotation dataset occurrence count | Keep as source metadata | Counting article mentions as times spoken |
| Same fact-check in several indexes | One review with several discovery paths | Treating aggregation as independent corroboration |
| External reviewer uses a rating scale | Preserve attribution and original wording | Normalizing to an unsupported person score |
| Evidence from another year | Scope mismatch/unresolved | Reusing a superficially similar fact-check |
| Revised primary dataset | New revision and dependent re-review | Keeping stale numerical findings current |
| Prediction not yet due | Pending outcome record | Labeling the forecast false in advance |
| Opinion/value judgment | Retain utterance; distinguish checkability | Forcing preferences into empirical verdicts |
| No evidence found | Unresolved, with searched sources | Converting absence of retrieval into falsity |
| Rights expiry | Block new dependent use; enforce retention workflow | Continuing publication through an old cache |
| Source unavailable | Availability state and coverage gap | Treating missing access as proof of absence |
| Paid vendor has no supplied schema | Access-dependent contract task | Shipping guessed endpoints as working integration |
| Source text contains instructions | Treat as data; enforce tool policy | Prompt injection changing rules or leaking secrets |
| Model returns invented source ID | Reject output | A plausible-looking uncited finding |
| Concurrent reviewer edits | Revision conflict and explicit reconciliation | Silent last-write-wins evidence loss |
| Correction complaint is unverified | Preserve report and triage | Automatically rewriting or ignoring the complaint |
| Real subject mixed with synthetic fixtures | Separate workspaces and visible flags | Publishing fabricated test findings |

### 20.1 Decisions recorded for the initial release

A single local store is chosen to make the evidence chain runnable without infrastructure
provisioning. A typed generic revision ledger is chosen to preserve record history and
avoid destructive updates. Exact reviewed coordinate deduplication is chosen over a
fragile automatic perceptual merge. Source clients are fixed-origin and metadata-oriented
rather than an unrestricted crawler. Generative reasoning and publication remain out of
the default execution path. Commercial sources are documented contracts rather than
empty adapters that return successful-looking fabricated data.

These are scoped engineering choices, not claims that the target problem is fully solved.
Each decision has an explicit extension path in the backlog. Replacing a reference
component must preserve its data semantics, negative tests, provenance, and independence.


---

## 21. Optional integrations without project coupling

### 21.1 Ports, not inherited infrastructure

The target defines optional ports for source discovery, source acquisition, speech-to-text,
diarization, source/context retrieval, candidate-claim extraction, prior-review matching,
notification delivery, and publication export. An adapter implements one port through
its own configuration and tests. None may assume another application's database schema,
identity namespace, graph structure, deployment network, or private repository exists.
A local no-provider configuration must continue to run the reference ledger.

The generic retrieval request includes workspace scope, query, permitted source IDs,
record/revision filters, time/scope constraints, result limit, and desired evidence kinds.
The response includes candidate canonical record IDs, source revisions, locators, excerpts,
retrieval method, and limitations. The ledger rechecks visibility and currentness before
using those candidates. Retrieval relevance is not factual support or semantic equivalence.

### 21.2 Model and speech contracts

A speech port receives an authorized asset reference, local/object-store handle provided
outside model text, range/timebase, language hints, preprocessing configuration, and a
model profile. It returns transcript/diarization candidates with input hash, engine/model
version, segments/words, local labels, timing precision, and warnings. It does not return
confirmed real-person identities without a separate reviewed mapping record.

A claim-extraction port receives exact source utterances and context and returns proposals
with grounded spans, speech acts, scope hypotheses, unresolved fields, and model provenance.
An evidence-research port returns cited candidate evidence and analysis of compatibility.
Neither port can write a completed review, alter access rights, or publish. The application
validates returned IDs and limits before storing proposals.

### 21.3 Export contract

A private research export contains record types, stable IDs, revisions, parent references,
source provenance, exact text when permitted, timebase information, scope, reviewed findings,
limitations, and correction/coverage metadata. A consumer must not turn an external review
or candidate attribution into an approved internal finding. A public export is a separately
approved snapshot with explicit content permissions and withdrawal support. The current
JSON export is a private operator backup, not a publication-ready external API product.

### 21.4 Future authorization of integrations

Before enabling an external adapter, record its contract, data sent, secrets location,
allowed operations, provider retention terms, failure behavior, costs, version policy,
and evaluation evidence. Test it in an isolated workspace. Removal of the adapter must
not make canonical source records unreadable. If the owner later authorizes interoperability
with another product, implement a new explicit adapter and mapping specification instead
of silently grafting that product's schema into this repository.


---

## 22. Reference limitations, unresolved decisions, and next gate

### 22.1 Implemented does not mean production-complete

The reference implementation provides a concrete storage/API/CLI/inspection workflow,
source-shaped parsing, bounded metadata clients, local media utilities, optional speech
calls, and synthetic correctness tests. It is useful for inspecting source formats,
prototyping the investigation chain, testing provenance rules, and developing later
workers. It is not a complete autonomous crawler, a reviewed real-person corpus, a
public fact-checking publisher, or a multi-user production deployment.

Exact-coordinate duplicate grouping does not solve near-duplicate alignment. Reviewer
strings are single-owner attestations rather than independently authenticated reviewer
roles. Root-array JSON import is bounded rather than a fully streaming array parser.
The raw-file receipt is returned but not fully indexed as its own canonical record.
The queue library is not wired into a scheduler/outbox executor. The operator UI lacks
waveform editing, synchronized transcript playback, and full review forms. Retention,
public withdrawal, prediction outcomes, production RLS, and live provider QA are planned.

### 22.2 External validation still required

Source network smoke requests for a GDELT sample and AAPB metadata failed because the build
runtime could not resolve hostnames. Official documentation was reviewed through web
access, but this does not constitute successful programmatic integration from the runtime.
YouTube and Google Fact Check clients require owner-supplied credentials. Commercial
providers require actual access contracts. Optional speech models were not downloaded or
run. Docker and clean dependency resolution require a network-enabled target environment.
A resolved cross-platform hash lock must not be invented; the package records its tested
local versions and leaves a lock-generation gate explicit.

### 22.3 Questions resolved by defaults

The initial repository is private by default when published with the supplied script.
There is one owner workspace and no public publishing. All source connectors are disabled
until explicitly invoked/configured. The subject example has no inferred aliases, current
role, channel IDs, findings, or automatically authorized spend. Source rights start empty
unless the operator supplies a documented grant. The demo uses fictional data. These
choices allow work to proceed without silently assuming decisions that affect privacy,
rights, cost, or factual integrity.

### 22.4 Decisions for the next authorized pilot

Select the actual date window and source subset, confirm the subject identity references,
obtain a permitted original/copy pair, choose and validate the speech worker environment,
and define reviewer acceptance examples. Confirm retention and provider-transfer rights
before processing restricted material. Measure real schema shapes, audio quality, and
review effort. Use that evidence to prioritize the next tickets instead of treating the
number of nominal connectors as progress.

The next gate is successful, source-bound ingestion and review of a real authorized
appearance with a documented original/copy relationship. That gate can end with supported,
contradicted, mixed, unresolved, or no checkable claim findings. The required result is
an auditable research process—not a predetermined conclusion about the subject.


---

## 23. Shared proposition, claim-family, and evidence library

### 23.1 Why the unit of reuse changes

A person's ledger remains the entry point for inspecting public speech. It is not the
right boundary for storing research about a proposition. Two speakers can make the same
scoped assertion; one person can make it repeatedly; many copied clips can represent one
occurrence. Research should be linked to a shared proposition without conflating these
three situations. This extension adds a local, person-independent claim library inside
this standalone application. It does not connect to another application or database.

The library admits supported, conflicting, mixed, unresolved and not-checkable research
records, but these are existing attributed reviews—not classifications invented during
indexing. It has no global "lie" label and no intent inference. A quotation, a proposed
proposition, a review, a publication decision and an allegation of intentional deception
remain distinct objects. The library can be useful before any assessment is available.

### 23.2 Canonical objects and relationships

`Proposition` retains exact proposed text, kind and scope. `seed_observation_ids` is an
optional list of source leads that produced an imported candidate. It is not a claim
that the quoted person was identified in a recording. Ordinary `Occurrence` records still
connect a reviewed assertion to an accepted utterance with identity and event provenance.

`ClaimFamily` has a title, description, proposition IDs, grouping basis and reviewer.
It is explicitly a topical grouping: its `equivalence_asserted` field is fixed false.
Two members may conflict, differ in year, differ in denominator, or ask different factual
questions. Families allow navigation without erasing those distinctions.

`ClaimCard` is a revision-bound collection of reviewed findings about one proposition.
It references existing review IDs and supplies an explicit expiry, freshness rationale
and approver. It does not manufacture another verdict field. Its
`automatic_verdict_reuse` value is fixed false. Review records continue to point to their
exact supporting occurrence and evidence records. Provenance is not duplicated into an
unmaintained second graph.

### 23.3 Retrieval and matching

A SQLite FTS5 projection indexes current proposition text and scope. Index writes occur in
the same transaction as proposition revisions. Startup performs a one-time additive
migration and backfills existing propositions without changing canonical payload bytes.
`reindex-claims` reconstructs the projection. Search tokenizes and quotes user terms;
raw FTS operators are never interpolated into executable query syntax. The result limit
is bounded. Indexed claim-card and correction lookups avoid a whole-card scan per hit.

FTS relevance is not a truth probability. This release retrieves lexical candidates; it
can miss paraphrases. Vector retrieval, multilingual semantic normalization, approximate
entity resolution and a production-scale search service remain future adapters. A large
benchmark of locally generated rows tests indexing mechanics, not the completeness or
correctness of real-world retrieval.

An optional Jev request compares a new proposition with a bounded candidate set. The
state contains assertion text and scope, not the speaker's political affiliation or
person-level reputation. The options are same scoped assertion, related but different,
unrelated and uncertain. Numeric compatibility, dates and final transition decisions
remain code-controlled. A semantic answer cannot override a structured scope mismatch.
No matching call merges propositions, publishes a review or updates a person's findings.

### 23.4 Scope compatibility is a hard boundary

The expanded scope includes entity, metric, geography, period, unit, baseline, comparator,
quantity, definition, polarity, conditions, population, accounting basis and document
version. Existing files missing new fields remain readable. Missing fields block the new
reuse-candidate gate; they are never interpreted as wildcards. `not_applicable` must be an
explicit reviewed interpretation, not a blanket migration default for unknown facts.

For example, "spending increased" can refer to nominal totals, inflation-adjusted totals,
per-person amounts, an authorization, an appropriation or actual payments. A topical
match does not resolve this. Changing polarity or a conditional qualification can create
a different proposition even when almost all tokens overlap. Exact scope agreement is
necessary for the candidate gate, but not sufficient proof of semantic equivalence.

### 23.5 Freshness, corrections and conflicts

`card_status` evaluates current dependency revisions and rights, expiry, open corrections,
canonical scope completeness and disagreement between referenced review findings. It
reports every blocked reason and returns the original references. It does not silently
choose one of several conflicting findings. A prior conclusion may be displayed as a
historical attributed record while being ineligible for current reuse.

A reported correction is enough to pause reuse while it is investigated. Verified and
reported corrections remain open until an operator records a dated resolution. Revising
a target does not automatically mean the correction was resolved. The correction
workflow records the reasoning and reviewer. Changed source records invalidate dependent
profiles, cards and model decisions through the existing revision graph.

Freshness is explicit and domain-specific. A historical event record may remain useful
for years, while a current-office-holder or rolling economic measure may need rapid
refresh. This release does not derive trustworthy expiry dates automatically. An operator
sets an expiry and its rationale; the application enforces it.

### 23.6 Bulk candidate seeding

`seed-claims` accepts a versioned JSONL interchange with `native_id`, `source_url`,
`claim_text`, optional scope and optional attributed speaker. Gzip and bzip2 inputs are
supported through the existing bounded reader. Original bytes are retained under a
checksum. Each accepted row creates a source quotation lead and an ambiguous proposition,
with no occurrence, no confirmed identity and no review finding. The supplied
`attributed_to` value remains an unverified publisher attribution.

Unknown fields such as `finding` are rejected. This is intentional: an imported label
must not become the application's own factual conclusion. External fact-checks continue
to enter through their attributed observation/review workflow. Every native source needs
an authorized transformation into the seed interchange; there is no universal scraper.

Identical text and identical stored scope share a seed proposition ID. Different wording
or different scope do not auto-merge. New source leads can add a provenance revision;
that deliberately invalidates dependent cards until revalidation. Import receipts record
limits, per-row errors and partial commits. A completed bounded batch is not a claim that
a publisher's corpus was exhausted. Retained observations may survive a rejected
proposition row and remain inspectable for repair.

### 23.7 Acceptance boundary

The executable path covers indexing, bounded imports, candidate search, scope gates,
optional typed comparison, review-card status and correction blocking. It does not
populate a complete world knowledge base, determine truth from language style, infer
intent, or automatically reuse a review for a new person's utterance. The operator can
reuse the underlying research after confirming applicability and recording the new
assertion context. That is where the saved research effort becomes auditable.


---

## 24. Learned speaker-language profiles

### 24.1 Purpose and limits

A language profile is a retrieval instrument for locating likely speaking regions in
captions. It is not biometric identification, authorship proof, a personality assessment
or evidence about the truth of any statement. The target may use unusual phrases once,
common phrases often, or another person's words while quoting them. A language signal
therefore controls inspection priority, not confirmed identity.

"Prefix" and "suffix" in the initial feature implementation mean turn-opening and
turn-closing word sequences, not morphological affixes. The implemented categories are
opening, closing and recurring phrase. More abstract concession, pivot, rebuttal and
rhetorical-structure categories are specified as future evaluated features; this release
does not pretend that every such category has a trained detector.

### 24.2 Training evidence contract

`SpeakerProfile` references a person, explicit target utterance IDs and explicit
background utterance IDs. Each example must be an accepted utterance with a confirmed
speaker mapping, reviewed appearance/context, current dependencies and permission to
learn the profile. A proposed localization window cannot enroll itself. A model's
high score cannot turn a candidate utterance into a training label.

The background class must exclude the target. It should contain people appearing on
similar programs, discussing similar topics and represented by similar caption sources.
Operators select that comparison set; software does not infer affiliations or choose
people based on political categories. Narrow or unrepresentative comparison data remain
a stated limitation even if the profile meets its minimum event counts.

### 24.3 Reproducible feature extraction

The current tokenizer uses Unicode normalization, case folding and word extraction while
retaining apostrophes. It is versioned and works beyond ASCII, but is not a multilingual
linguistic analyzer. The original transcript text is unchanged. Ngram lengths, minimum
support, minimum event counts and maximum feature count are explicit configuration.

Each accepted turn contributes opening and closing ngrams and interior phrase ngrams.
Statistics use event presence: a feature seen several times in the same original event
contributes one event to that speaker class. Exact repeated turn text within one person
and event is tracked as duplicate training input. Copies and short reposts therefore do
not amplify the feature merely by appearing on several websites.

For feature support a of n target events and b of m comparison events, the implementation
uses a smoothed log-odds difference:

`log((a+0.5)/(n-a+0.5)) - log((b+0.5)/(m-b+0.5))`.

This is a discovery weight, not an identity probability. Features below the minimum
independent-event support or with nonpositive contrast are excluded. Remaining features
are deterministically ordered. At localization time, nested ngrams are not added as
independent evidence; the maximum matching phrase weight is used for the simple baseline.
The baseline is intentionally inspectable rather than presented as a fitted classifier.

### 24.4 Provenance and readiness

The profile retains contributing IDs/revisions, retained and duplicate examples, target
and background event IDs, configuration, extracted features and algorithm version.
`research_ready` means only that the configured sample/support conditions are met. It
is not a deployment approval or a calibration certificate. Insufficient data produces
`cold_start`. Cold-start localization falls back to complete audio processing.

The server recomputes profile-derived fields during validation. A caller cannot submit a
made-up phrase weight while keeping genuine source references. Record updates use
optimistic concurrency. The dependency graph marks a profile stale when its source
identity, transcript, rights or accepted turn changes. Related localization and model
records become stale as well.

### 24.5 Incremental learning and holdouts

`refresh-profile` rebuilds an existing profile from current accepted target turns. It
preserves a curated background set unless the operator explicitly supplies comparison
person IDs. Explicit holdout events are excluded from both classes. Ineligible or stale
samples are reported rather than silently used. No utterance is automatically confirmed
by the refresh operation. A stale profile's configuration can be read for a rebuild, but
all new training evidence must independently pass current validation.

This is an explicit command/API operation, not an already deployed always-running learner.
The existing outbox can support a later worker that flags profiles for refresh after new
reviewed turns arrive. That worker must preserve curated source/domain constraints and
must not retrain from its own unverified detections. No online fine-tuning of Jev is
performed. Profiles are local data supplied as compact request context.

### 24.6 Evaluation requirements

Training, threshold tuning and final testing must be split by original event. Near-identical
clips of one episode belong to the same split. Evaluate short turns, long answers,
interruptions, quoted speech, hosts imitating a catchphrase, speech-recognition errors,
new topics, new dates and new programs. Report target-time coverage and turn coverage in
addition to the fraction of audio selected. A high score on shuffled windows from the
same episode is not evidence of transfer to unseen appearances.

Separate drift in a person's language from drift in the captioning system. Changing
transcription punctuation can change apparent openings and endings. Model-based semantic
features must record their provider/question revision and be reevaluated before being
used to reduce audio processing. Human confirmation remains the boundary for identity.

### 24.7 Implementation map

`profiles.py` implements training, deduplication, feature scoring and refresh.
`acceleration_models.py` provides the profile contract and configuration.
`acceleration_service.py` verifies reproducibility and dependency revisions.
The authenticated interface displays the contributing event counts, category, phrase
and support values. Detailed JSON retains the full provenance. The interface intentionally
does not display a personal honesty score or an unsupported identity percentage.

Research basis: word-use differences can carry speaker information, but transfer to
short broadcast turns is an empirical question. See [Doddington's linguistic speaker
recognition paper](https://www.isca-archive.org/eurospeech_2001/doddington01_eurospeech.html).
The implementation here is an original reference baseline, not a reproduction of the
paper's benchmark or a claim to match its results.


---

## 25. Transcript-first speaker localization and audio-work planning

### 25.1 Entry point and state progression

A localization request identifies an existing profile and a timestamped transcript tied
to a known-duration asset. Its output is a `LocalizationRun`, not an utterance or
speaker mapping. Candidate windows pass through lexical screening, optional semantic
screening, interval merging and context padding. Only subsequent acoustic/manual review
can produce accepted speaking turns.

The core state progression is:

`unprocessed -> candidate or audit -> audio inspected -> attribution proposed -> human confirmed`.

A low-scoring region remains unprocessed. It is not a finding that the target was absent.
A provider error is an unavailable evaluation, not a negative identity answer. The
profile itself is not updated when a window is selected.

### 25.2 Window construction

Windows use the original asset's integer millisecond timebase and half-open intervals.
The default window is 30 seconds with a 15-second stride. Each contains intersecting
caption segments; the transcript is never rewritten to make the window look cleaner.
Window and stride configuration are bounded and stride cannot exceed window length.
Work exceeding the maximum number of windows falls back to a complete recording plan.

Window boundaries need not coincide with speaking turns. A prefix feature seen inside a
window is therefore a candidate clue, not proof that the window starts with the target.
The following question, a host handoff and another participant's interruption can all
be inside one window. Every selected window retains segment indices and reasons.

The baseline checks learned phrases and a narrow name-plus-punctuation handoff pattern.
A name mention is never confirmed identity. Aliases are operator-provided and escaping
prevents names from becoming executable regular expressions. The heuristic's sensitivity
to punctuation is documented rather than hidden as a calibrated probability.

### 25.3 Optional semantic screening

Jev receives compact profile features and a bounded batch of candidate text windows.
Each question explicitly points at its window in state; question IDs alone are not used
as natural-language instructions. The full bounded set can be screened, rather than
restricting semantic analysis to keyword-positive windows and permanently missing
uncharacteristic speech. Each result is a raw provider signal with model/question
revision, not a calibrated identity probability.

Semantic and lexical positive signals are combined conservatively as candidate reasons.
They are not multiplied as independent probabilities. A high lexical score is not
vetoed by a model's low signal. Missing window answers, incompatible response contracts,
failed transport or exhausted request budgets retain a full-audio fallback. A known
insufficient batch budget is detected before sending paid requests.

### 25.4 Audit and caption gaps

A deterministic sample of low-scoring windows is included for audit. The default is ten
percent, rounded upward, with an explicit seed. Selection depends on source/profile
revision hashes so a run is reproducible. The audit is a safety net and evaluation input,
not a guarantee that no target turn was missed.

Uncaptioned intervals are separately retained as caption gaps. They are not assumed to
be silence. Gaps enter the selected work and receive conservative context treatment.
Sparse captions may consequently eliminate most expected savings. That is an honest
result: captions that do not cover the recording cannot justify skipping unknown audio.
A future VAD-assisted gap classifier requires its own validation and is not implemented.

### 25.5 Interval algebra and mode semantics

Adjacent or overlapping work is merged before duration/cost calculations. Padding is
applied with bounds at zero and the asset duration. Work for multiple people can be
combined per asset; it is never shared across unrelated asset timebases based only on
similar wording. If selected work approaches the configured full-processing fraction,
the router chooses the complete asset instead of many nearly exhaustive clips.

`shadow` is the default. It records a proposed smaller plan but selects the whole asset
for actual work. It is suitable for gathering labels and estimating what would have been
skipped. `assist` exposes the smaller research workload and keeps all unprocessed ranges
visible. It is an operator-selected research mode, not an automatically certified
production mode. This release has no hidden calibrated-auto mode.

`proposed_audio_ms` and `selected_audio_ms` are different fields. The reported reduction
fraction is the fraction of asset duration excluded from the actual selected plan; it
is not a measured reduction in spending, a proportion of the target's speaking time or
an accuracy measurement. `coverage_recall` remains null until separately evaluated with
labels. `identities_confirmed` and `probability_calibrated` are fixed false.

### 25.6 Failure matrix

| Condition | Required behavior |
|---|---|
| Cold or empty profile | Full asset selected; cold-start reason recorded. |
| No positive text candidates | Full asset selected; no absence conclusion. |
| Excessive window count | Bounded work stops; full-asset fallback. |
| Missing caption regions | Unknown regions included for audio inspection. |
| Jev credentials absent after explicit enable | Recorded unavailable decision; full fallback. |
| Malformed or incomplete Jev response | Raw receipt retained; no fabricated negative; full fallback. |
| Rights do not permit provider submission | Request rejected before sending any text. |
| Source revision changes | Prior plan/decision becomes stale; rebuild required. |
| Many tracked people cover most audio | Merge once per asset rather than process repeatedly. |

### 25.7 Downstream execution

The local execution command validates source bytes against the registered asset hash,
checks current permissions and the plan revision, creates each selected clip, and records
its source offset. Optional speech recognition/diarization runs only on those clips.
Local speaker labels are namespaced by clip. `speaker_0` from two different clips does
not automatically represent the same person.

Results retain clip-relative timestamps plus source-coordinate fields. No code assumes
that the crop's time zero is the original recording's time zero. Exact turn boundaries
and overlapping speech remain review responsibilities. Word-level forced alignment and
cross-window acoustic identity clustering are not part of this release.

### 25.8 Synthetic acceptance scenario

The demonstration contains a 600-second caption timeline, separate training events and
two labeled target turns. It generates shadow and assist plans without a provider call.
It reports selected time, captured target time and unprocessed regions from the actual
result. Its precise numbers can change when parameters or code change and must therefore
be read from the generated validation report rather than treated as a marketed promise.
The demonstration neither enrolls nor attributes any real person.


---

## 26. Official TypeSafe Jev adapter, capture discipline and decision caching

### 26.1 Correct provider boundary

The optional adapter targets `https://api.typesafe.ai/v1/systemone`, as documented in
TypeSafe's [official API reference](https://docs.typesafe.ai/api). The community article
supplied during planning links to a separately branded service and is not the authority
for this integration. No API key is sent to that third-party endpoint. The endpoint is
fixed in code rather than accepted from an API request or source document.

The default model configuration is the versioned `jev-1.13.0`, checked against
[TypeSafe's model documentation](https://docs.typesafe.ai/models) on September 27, 2026.
An environment setting can select a different model, but a pinned response must resolve
to the requested version. Aliases can move and are excluded from persistent answer-cache
reuse. The application runs without a key, without remote retrieval and without Jev.

Jev is text-only at the documented boundary. It receives justified transcript text and
structured context; it does not listen to audio, identify faces, run diarization, or
produce verified scientific/legal/economic facts merely because its output is typed.
Language profiles are local context, not per-account fine-tuning of the provider model.

### 26.2 Two bounded purposes

`speaker_localization` asks whether each text region warrants inspection for a plausible
target speaking turn. `claim_matching` compares scoped assertions without deciding their
truth. Each purpose has a versioned question contract and stable source bindings. Neither
purpose can set a reviewer, publish an assessment, merge canonical entities, authorize
media acquisition or modify a confirmed identity mapping.

Question batching reuses a compact state across independent checks. Budget calculations,
interval merging, numeric comparisons, source permissions, dates and execution decisions
remain ordinary code. TypeSafe's [documented limitations](https://docs.typesafe.ai/model-jaggedness/jev-1.13)
reinforce this division. Response confidence and raw answer values remain distinct from
locally measured identification reliability.

### 26.3 Input authorization and size budgets

`SL_ENABLE_JEV=1` is required for the configured live client; the default is off.
`TYPESAFE_API_KEY` is server-side only. Before a request, the application walks current
input dependencies and requires `send_to_provider` on each source rights grant. Learning
a phrase profile is not permission to send the underlying material to a remote service.
The same check runs before cache reuse so revoked/expired material cannot bypass policy.

Requests are limited by byte count, question count, batch count, timeout and attempts.
These are explicit engineering budgets, not a claim that bytes equal provider tokens.
The provider's returned usage is retained where valid. Unknown usage after a failed call
is unknown cost exposure, not zero cost. Pricing is a user-supplied input to the cost
estimator; the release does not hard-code a lasting commercial promise.

### 26.4 Capture before interpretation

For each attempt, response bytes, HTTP status, truncation flag, request metadata,
checksums and capture time are committed to `provider_receipts` before JSON decoding,
schema validation or semantic use. Authentication headers are not included. A transport
failure has an explicit empty-body receipt. Capture failure stops processing; the code
does not proceed with an unrecorded semantic decision.

Private request metadata contains the actual supplied state and may be sensitive.
Receipts belong in the private workspace, are covered by backup/retention policy and
must not be exposed through a public static directory. `verify_provider_receipts` checks
stored byte hashes. Hash consistency is not an independent witness against an
administrator who can rewrite the entire database and audit chain.

### 26.5 Contract validation and quantization

JSON duplicate keys and non-finite literals are rejected. Numeric values cannot be
Booleans, strings, infinities or out-of-range probabilities. Question IDs, answer types,
choice options, score legends, usage fields and resolved model must match the request.
Truncated responses cannot become available decisions. Captured request metadata is
checked against the stored decision bindings and state hash.

The adapter preserves raw Choice/Score distributions and reported scores. It does not
recompute the provider's confidence or demand exact equality between an independently
rounded score and an expectation calculated from rounded probabilities. Narrow
provider-scoped two-decimal compatibility bounds produce explicit warnings; large or
incompatible residuals produce an unavailable result. Values are not silently normalized.
Tests cover this distinction so arithmetic fixture assumptions cannot discard useful
provider evidence without explanation. Noul outputs have their own direct range check.

### 26.6 Fault semantics and retry policy

The outcome is either available or unavailable, with an explicit error code. An
unavailable decision has no semantic answers. Missing credentials, timeouts, model drift,
unknown labels, malformed JSON and incomplete answer maps never become a zero-valued
speaker signal or a "different claim" answer.

Retries are bounded and limited to transport/transient HTTP conditions, including rate
limit and overload responses. Retry-After is honored within the configured maximum.
Schema failures are not retried as network faults. Each attempt receives its own capture;
repeated attempts may incur cost. After a failure the application preserves deterministic
work and routes localization to complete audio inspection. There is no fabricated model
fallback presented as a successful evaluation.

### 26.7 Revision- and rights-aware caching

The cache key includes purpose, state, questions, version, input IDs/revisions, official
endpoint, requested model and validator version. Reuse requires an available decision,
a pinned model, unexpired TTL and current dependencies/permissions. Changing the profile,
transcript, proposition, scope, questions or rights invalidates applicability. The cache
is an optimization over canonical records, not the system of record for truth.

All cache-hit responses preserve the original decision ID and receipt history. Changing
the cache TTL does not rewrite a past model response. Source text is untrusted: instructions
embedded in captions or quotations have no permission to change destinations, reveal
credentials, approve findings or trigger unrelated tool calls.

### 26.8 Release evidence

The included automated tests exercise the HTTP boundary with mocked responses, retries,
raw capture, numerical edge cases, permission rejection, input changes and failure
fallback. No paid live-provider benchmark was run for this release. The adapter must be
verified with authorized real payloads before its signals are used to reduce production
processing. See [confidence documentation](https://docs.typesafe.ai/confidence) for the
provider's terminology; local calibration remains a separate acceptance task.


---

## 27. Evaluation, calibration diagnostics, processing cost and promotion

### 27.1 What must be measured separately

Three uncertainties must remain distinct: whether a text window resembles the target's
language, whether the target actually speaks anywhere in that window, and whether each
word in a final turn is correctly attributed. A fourth question is whether a scoped
claim is supported by evidence. Good performance on any one task does not certify the
others. A language-style score never affects the factual assessment of an assertion.

The reference release reports window-selection mechanics, not deployment readiness.
Explicit labels are required to calculate target-speech recall. A planned reduction in
processed minutes is not an observed reduction in cost. A model's Noul value is not
labeled a calibrated probability of speaker presence without appropriate held-out tests.

### 27.2 Event-separated evaluation corpus

Use original events as the grouping unit for training, validation and test. Copies,
excerpts, syndicated recordings and transcriptions of one event must stay in one split.
Hold out new programs, dates, caption systems and topics where feasible. Define target
presence using inspected audio and retain uncertain labels rather than forcing them into
positive/negative examples. The supplied fixture is fully synthetic and never substitutes
for this corpus.

The evaluation command rejects a test event appearing in the profile's target or
background event list. Label files identify the exact asset timebase. A label file for
a different asset is refused even if its durations happen to be equal. Labels supplied
by an operator remain operator assertions; the software cannot prove that omitted speech
was genuinely absent or that the labels cover the entire recording.

### 27.3 Localization measurements

Target-time recall is captured target milliseconds divided by total labeled target
milliseconds. Time arithmetic uses interval unions and intersections so overlap cannot
inflate the numerator. When no target speech is labeled, recall is null rather than a
misleading perfect score. Turn coverage uses the distinct supplied turn intervals and
is reported separately from total time.

Also report selected audio duration, missed labeled target time, audit-window selection,
caption gaps, fallback reasons and unprocessed ranges. Deployment approval remains false
in the current evaluator. A test with incomplete labels can still be useful for debugging,
but must not be used as evidence of whole-recording recall.

### 27.4 Probability diagnostics, not automatic calibration

`calibration-report` computes observed frequencies by signal bin, Brier score and expected
calibration error from supplied Boolean labels. It refuses training/test event overlap.
It does not fit or deploy a calibrator, choose a threshold, estimate confidence intervals
or certify that a model is calibrated. Sparse bins and within-episode correlation are
visible limitations. Group-aware bootstrap intervals and a fitted calibration artifact
remain later work.

Model version, question version, profile revision, source format and label policy must
be fixed when comparing candidates. Evaluate separate thresholds for candidate screening
and identity confirmation. Screening prioritizes recall; final attribution requires much
stronger evidence. Thresholds should be selected on validation data and tested on an
independent event set, not tuned to the final test episodes.

For the underlying concept see the primary [scikit-learn calibration documentation](https://scikit-learn.org/stable/modules/calibration.html).
The current report is a small independent diagnostic implementation rather than a claim
that a supervised calibrator has been trained.

### 27.5 Cost model

The estimator accepts original duration, selected duration, price per processed audio
minute, screening input tokens, price per million input tokens, verification cost and
additional overhead. All quantities must be finite and nonnegative; selected duration
cannot exceed the original. It calculates the full-audio baseline and the complete
supplied optimized-cost estimate. Negative estimated savings are valid and instructive.

`baseline = original_minutes * audio_unit_cost`

`optimized = selected_minutes * audio_unit_cost + screening + verification + overhead`

The result identifies the lower estimated cost route without claiming a measurement.
Currency must be consistent across inputs. Storage, download, caption acquisition,
retries, GPU startup, human review, retranscription and reprocessing after corrections
must be included in the operator's parameters when relevant. Cost examples in the
repository are fictional inputs, not provider quotes.

### 27.6 Baselines and ablations

Compare whole-file diarization, phrase-only localization, phrase-plus-Jev localization,
audio-first target-speaker approaches and combinations appropriate to available data.
Measure p50/p95 latency, actual billed usage, errors, preserved target time and accepted
turn accuracy. Test cold start and sparse captions. Do not charge every rejected window
as zero compute when it required model processing. Do not attribute a speedup solely to
Jev when it comes from cached captions or a smaller test corpus.

When many tracked people appear in one episode, combine their selected intervals before
cost estimation. A full recording can be cheaper than repeated crops once overhead and
overlap are counted. Existing derivations should be reused only under matching source
hash, timebase, model configuration and rights. A cache for one recording cannot satisfy
another recording merely because the same sentence occurs.

### 27.7 Promotion plan

Stage one is offline synthetic and adversarial contract testing. Stage two uses authorized
real recordings in shadow mode with independent labels. Stage three exposes assist mode
to an informed operator, with rejection audits and complete fallback. A later production
automation gate requires written minimum sample sizes, coverage targets, confidence
intervals, a documented tolerated miss rate, verified corrections propagation and a
rollback switch. This release does not invent those deployment thresholds.

Adaptive models or changing language profiles must not silently reduce the audit rate.
A profile upgrade can be rolled back by restoring the previously evaluated configuration
and recomputing current plans. Historical records remain append-only. Cost optimization
must never rewrite the quotation, the speaker evidence or the independent occurrence
counts to make an outcome appear more favorable.


The implemented cost command also accepts `screening_output_tokens` and `price_per_million_output_tokens`; input-only pricing must not silently stand in for the full bill. Failed or incomplete provider responses may have unknown billed usage; account for that separately rather than treating them as free.


---

## 28. Local media execution, additive migration and v0.2 release boundary

### 28.1 Selective media execution

`process-localization` accepts a current localization-run ID, a local media file, a new
output directory and an allowed media root. It validates the file checksum against its
asset, checks current provenance and permissions, and creates only the run's selected
intervals. Shadow plans therefore process the entire recording; assist plans process
the proposed smaller workload. Both input and output must resolve inside the allowed
root. The source is never overwritten and an existing output directory is refused.

The command writes a manifest before work begins and updates it after each completed
clip. On failure it leaves a failed manifest and the completed items for inspection.
There is no hidden automatic resume that could confuse old results with a changed source.
FFmpeg re-encodes rather than pretending keyframe-only copying is exact. Audio-only M4A
or WAV destinations no longer inherit a video mapping. Each real clip is probed and a
large duration mismatch stops processing.

### 28.2 Coordinate discipline

A media result retains clip-relative coordinates and the source start offset. Derived
segment and diarization-turn metadata also carry source-coordinate fields. Local speaker
labels are prefixed by the window ID; `speaker_0` in a later crop is not assigned to the
same person by name equality. These outputs remain candidates and are not automatically
imported as accepted utterances.

The first implementation validates requested interval bounds and clip duration. It does
not certify codec sample-exact alignment, automatically reconcile words that cross a
crop boundary, or verify every model timestamp against the waveform. Forced alignment,
source-coordinate word indexing, edited-compilation mapping and cross-window acoustic
clustering remain separately evaluated work. The manifest makes that boundary visible.

### 28.3 Optional acoustic comparison

`speech.verify_speaker_clips` wraps a pre-provisioned local SpeechBrain ECAPA model. It
requires local clip files, a pinned model-directory revision and explicit audio/biometric
processing permissions. It returns cosine similarity and file hashes, not a named-person
identity probability. The model's binary prediction is not used to approve a mapping.
No weights are bundled and the function does not download a model on its own.

The operator must select suitable reference and candidate clips and establish their
source provenance. The utility itself does not prove who is in the enrollment recording.
Replay, impersonation, overlap, short clips and cross-channel recording differences are
review concerns. Local file and permissions checks are implemented; live model inference
was not run in this release. Consult the primary [SpeechBrain model card](https://huggingface.co/speechbrain/spkrec-ecapa-voxceleb)
for the inference interface and its stated out-of-domain limitations.

### 28.4 Database upgrade and rollback

The v0.2 store creates an FTS projection, provider-receipt storage, migration tracking
and lookup indexes. Original record revisions, hashes and audit history are not rewritten
merely to add missing optional fields. A native SQLite backup must be taken with the old
application stopped or through its online-backup command before first opening the real
workspace in the new version. Run integrity checks before and after the upgrade.

New Scope fields default to unknown when reading legacy data. They are not silently
filled with `not_applicable`. Old cards/claims may consequently fail new reuse-candidate
checks until reviewed. Historical source records remain inspectable. Updating a legacy
record creates a normal new revision with the expanded schema and expected-revision guard.

Rollback restores the pre-upgrade database backup and the previous code together. Do not
run old code against new extension records and assume it understands them. Preserve the
v0.2 database separately before rollback so new research is not silently lost. JSON
exports are private inspection backups; native SQLite backup is the tested complete
workspace copy, including receipt tables. Generated search indexes are rebuildable.

### 28.5 Security and retention

The application remains an authenticated single-owner research workspace. No deployment
or credentials are borrowed from another project. The expanded API exposes profile
build/refresh, local plan generation, claim search/card inspection and explicitly enabled
Jev analysis. Browser credentials stay in memory, never browser persistent storage.
Expensive local media processing remains a CLI operation rather than accepting arbitrary
server paths from browser requests.

Provider receipts may contain licensed transcript text. Configure retention and deletion
before operational use; this release does not implement an autonomous purge daemon or
claim cryptographic erasure from backups. Rights expiration blocks new processing and
reuse, but does not automatically delete every retained copy. Such deletion requires an
operator-managed retention workflow and backup policy. No third-party media or biometric
reference recordings are bundled.

### 28.6 Scope of delivery

The upgrade implements local claim indexing/bulk seeding, evidence-card freshness and
correction gates, reproducible language profiles, explicit profile refresh, transcript
window planning, audits/fallbacks, an optional typed decision adapter/cache, selective
local media execution, advisory local speaker comparison, evaluation diagnostics, cost
calculation, CLI/API entry points and inspector views. It preserves all original named
source worksheets and connector contracts.

Not delivered as completed capabilities: licensed access to all sources, full web/video
harvesting, a complete corpus of real pundit statements, an automatically fitted speaker
classifier, full production search at unbounded scale, autonomous fact adjudication,
intent detection, universal person scores, public publishing or unattended deployment.
The distinction is enforced by default modes and record contracts, not only prose.

### 28.7 Verification record

Use `docs/VALIDATION_REPORT.md` and machine-readable files under `validation/` for the
actual release results. A successful mock validates client behavior, not the provider's
real latency or accuracy. A successful synthetic audio clip validates the execution
path, not real panel-discussion diarization. A blocked browser navigation is not a visual
pass. The release process records these limits rather than converting missing tests into
claims of completion.


JSON backup version 2 encodes provider receipt bytes as `body_base64` so even malformed non-UTF-8 responses survive export exactly. The native SQLite backup remains the supported database-restore mechanism; JSON export is inspectable interchange, not an implemented automatic restore command.
