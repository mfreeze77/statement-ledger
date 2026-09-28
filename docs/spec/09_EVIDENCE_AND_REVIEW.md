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
