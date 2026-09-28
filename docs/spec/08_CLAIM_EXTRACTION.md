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
