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
