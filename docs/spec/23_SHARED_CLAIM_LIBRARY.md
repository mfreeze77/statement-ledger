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
