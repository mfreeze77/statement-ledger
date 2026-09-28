## 14. Model orchestration, tool boundaries, and prompts

### 14.1 Provider-neutral roles

Use models only where they have a defined role: speech recognition, local diarization,
quote-to-window retrieval, claim candidate extraction, scope interpretation, evidence
search planning, source comparison, or draft explanation. Each role has a typed input,
output, model/prompt/configuration version, budget, provenance policy, and evaluation set.
The core runs without any generative-model credentials. The reference code does not
implement an automatic fact-adjudication model or silently fall back to one.

A small or inexpensive model may classify candidate tasks; a more capable model may
analyze difficult evidence. The design does not assume a particular vendor, current
model name, rate limit, or token price. Capability profiles and prices are runtime
configuration that must be checked against provider documentation when adopted. A
provider's marketed benchmark does not establish performance on panel-discussion audio
or the project's own claim-review corpus.

### 14.2 Context packs

An extraction context pack contains the exact utterance and nearby turns, source timebase,
reviewed identity status, event-date evidence, transcript revision, and allowed source
metadata. An evidence-analysis pack contains the scoped proposition, asserted occurrence,
primary evidence excerpts/locators, relevant prior-review provenance, uncertainty, and
known counterevidence. Do not include unrelated personal information or political
preferences. Do not use the speaker's ideology, party, or network as a feature of factual
correctness. Speaker identity needed for attribution is separate from claim evidence.

Context packs identify missing information explicitly. A model cannot fill a blank source
locator, invent a document, or turn an inferred date into a source fact. The returned
claim/evidence proposals must cite existing provided record IDs and spans. An output
validator rejects references not present in the permitted input or tool results.

### 14.3 Prompt and output rules

The extraction prompt asks for candidate propositions and speech acts, not a verdict.
The evidence prompt asks for a comparison under explicit scope, missing information,
and a list of source-grounded reasons. It must distinguish an external publisher's
assessment from a proposed internal assessment. The publication draft prompt may describe
only an already reviewed finding and its current citations; it cannot create a new
finding by writing persuasive prose.

All source text is untrusted data. Instructions found in a transcript, article, caption,
HTML comment, or document must not override the tool policy, change source scope, reveal
credentials, trigger external writes, or tell the system how to classify a person.
Source content is delimited and tools are provided through fixed, least-privilege
interfaces. Prompt injection defense is also enforced outside prompts: allowlisted
operations, bounded retrieval, schema validation, and explicit write approvals.

### 14.4 Caching and reproducibility

Cache by task type, exact input hashes/revisions, model version, prompt version, generation
settings, parsing version, and rights partition. Do not reuse a model result after its
underlying transcript, person mapping, evidence, or scope changes. Store the raw output,
validated output, rejection reason, retry count, usage, and tool trace where permitted.
A failed or unparsable model response becomes a failed proposal, not a positive result
from a fallback heuristic that hides the loss of evidence.

The operator can compare model proposals across versions on a held-out corpus. A model
upgrade requires regression testing on identity errors, negation, scope hard negatives,
source hallucinations, and correction propagation. Disagreement among models is not a
vote that establishes truth. A deterministic arithmetic or unit-conversion check should
be implemented as code rather than delegated to repeated free-form model judgments.

### 14.5 Optional speech adapters in this release

`speech.py` includes an optional faster-whisper call, a pyannote diarization call, and a
conservative segment-to-label overlap matcher. These use approved local files and rights
grants. They do not download source videos or assign a real person name. Model weights,
GPU runtimes, gated model permissions, and large optional dependencies are not bundled.
The test suite exercises adapter logic with fakes; actual model inference requires a
separate integration run with logged versions, input rights, and human-labeled evaluation.

The target isolated worker should record content hash, preprocessing, model weights
revision, dependency lock, hardware, timestamps, and any context retained across chunks.
Do not label a mocked adapter test as a successful speech-recognition benchmark.
