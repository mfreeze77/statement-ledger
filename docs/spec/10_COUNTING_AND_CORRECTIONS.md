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
