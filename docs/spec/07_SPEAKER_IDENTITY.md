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
