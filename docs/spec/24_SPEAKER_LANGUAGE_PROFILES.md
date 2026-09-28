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
