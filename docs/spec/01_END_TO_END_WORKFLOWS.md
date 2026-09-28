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
