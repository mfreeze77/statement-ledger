## 06. Media processing, timelines, and clipping

### 06.1 Preserve originals and probe before processing

An authorized asset is identified by retained source reference and, when local bytes
are used, a byte-level checksum. Record duration, container, audio/video tracks, sample
rate, channels, frame-rate/timebase information, and probe-tool version. Derivatives
never overwrite originals. The v0.1 CLI requires a registered asset checksum before
processing local media; matching it is a lineage check, not independent proof of rights.
Content acquisition and media probing are planned as durable jobs rather than API-thread
work in the production architecture.

Malformed media is untrusted input. The target worker has a bounded local input root,
no unrestricted network access, resource limits, a read-only source mount, controlled
output location, protocol restrictions, and explicit timeouts. The reference FFmpeg
utility restricts paths to a configured root and avoids shell interpolation, but it is
not a complete hardened decoder sandbox. Do not expose arbitrary media upload and
processing publicly until the worker-isolation gate is complete.

### 06.2 Locate broadly before clipping narrowly

An article quote or caption hit proposes a time window, not necessarily the final
utterance boundary. Start with generous context, identify the surrounding question and
responses, and process the full available episode when justified by the investigation.
Clipping every search hit first can remove qualifications and cause repeated ASR work.
Cache derivations by original asset hash, time window, model/configuration revision,
and preprocessing parameters. Never share a cache entry across unequal timebases or
rights partitions solely because the same words occur.

The reference `clip_plan` uses integer milliseconds and a configurable context padding,
defaulting to 15 seconds. That is an initial utility parameter, not a rule that 15 seconds
always preserves sufficient context. A question may begin minutes earlier. The target
ContextBundle stores explicit relationships to surrounding turns rather than only a
fixed padding number.

### 06.3 Separate source coordinates and event coordinates

Every timestamp has a coordinate system. Source time belongs to a particular media
asset. Event time belongs to the resolved original appearance. A derived excerpt can
start at source zero while corresponding to event time 20 seconds. In the reference
model, `event_time = source_time + reviewed_offset`. The offset requires reviewer and
evidence fields; an unaligned asset remains visible but its assertions are excluded from
aligned occurrence counts.

Constant offsets are insufficient for edits, speed changes, inserted advertisements,
montages, reordered segments, and missing portions. The target PiecewiseAlignment stores
source interval, event interval, transform parameters, direction, certainty, evidence,
and reviewer per piece. Gaps remain unmapped. A timestamp found in one upload cannot be
reused on another upload without a supported mapping. The system must not infer original
event date or duration from the upload's filename.

### 06.4 Transcription and timing precision

Use the original audio track when possible. Record channel extraction, resampling,
normalization, voice-activity detection, chunk boundaries, overlap, and language decisions.
ASR returns candidate words, not evidence that recognition is correct. Preserve engine
outputs before cleanup. Transcript correction creates a new revision. Word timestamps
must disclose their alignment source and precision; segment boundaries must not be
presented as exact word boundaries. Unalignable words need an explicit unresolved state.

WhisperX documents word alignment and diarization workflows but also describes limitations
with overlapping speech and some token alignments. It is a technical comparator and an
optional future integration path, not an accuracy guarantee. The reference implementation
supports timed text and standard ASR segment exports, plus an optional faster-whisper
adapter. It has not run downloaded speech models in the delivery environment. See
[WhisperX documentation](https://github.com/m-bain/whisperX) and
[faster-whisper](https://github.com/SYSTRAN/faster-whisper).

### 06.5 Produce two useful viewing ranges

Retain a speech range and a context range. The first highlights the target words; the
second helps a reviewer interpret them. A source-player deep link can be sufficient when
copying media is not permitted. A stored clip needs explicit derivation rights, and its
publication requires a separate right. The target clip manifest includes input/output
hashes, exact requested ranges, observed output duration, tool configuration, rights,
source revision, and any offset introduced by codec behavior.

The v0.1 utility re-encodes instead of treating keyframe stream-copy boundaries as exact.
Its test generates synthetic audio, clips a known interval, and probes the result. This
proves basic local execution and expected duration for that fixture, not frame accuracy
for every codec or variable-frame-rate recording. Output metadata and contextual review
remain release-gate requirements for the full media workflow.
