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
