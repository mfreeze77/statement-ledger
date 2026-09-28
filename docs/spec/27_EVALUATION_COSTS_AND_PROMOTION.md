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
