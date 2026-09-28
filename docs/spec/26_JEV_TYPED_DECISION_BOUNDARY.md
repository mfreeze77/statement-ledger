## 26. Official TypeSafe Jev adapter, capture discipline and decision caching

### 26.1 Correct provider boundary

The optional adapter targets `https://api.typesafe.ai/v1/systemone`, as documented in
TypeSafe's [official API reference](https://docs.typesafe.ai/api). The community article
supplied during planning links to a separately branded service and is not the authority
for this integration. No API key is sent to that third-party endpoint. The endpoint is
fixed in code rather than accepted from an API request or source document.

The default model configuration is the versioned `jev-1.13.0`, checked against
[TypeSafe's model documentation](https://docs.typesafe.ai/models) on September 27, 2026.
An environment setting can select a different model, but a pinned response must resolve
to the requested version. Aliases can move and are excluded from persistent answer-cache
reuse. The application runs without a key, without remote retrieval and without Jev.

Jev is text-only at the documented boundary. It receives justified transcript text and
structured context; it does not listen to audio, identify faces, run diarization, or
produce verified scientific/legal/economic facts merely because its output is typed.
Language profiles are local context, not per-account fine-tuning of the provider model.

### 26.2 Two bounded purposes

`speaker_localization` asks whether each text region warrants inspection for a plausible
target speaking turn. `claim_matching` compares scoped assertions without deciding their
truth. Each purpose has a versioned question contract and stable source bindings. Neither
purpose can set a reviewer, publish an assessment, merge canonical entities, authorize
media acquisition or modify a confirmed identity mapping.

Question batching reuses a compact state across independent checks. Budget calculations,
interval merging, numeric comparisons, source permissions, dates and execution decisions
remain ordinary code. TypeSafe's [documented limitations](https://docs.typesafe.ai/model-jaggedness/jev-1.13)
reinforce this division. Response confidence and raw answer values remain distinct from
locally measured identification reliability.

### 26.3 Input authorization and size budgets

`SL_ENABLE_JEV=1` is required for the configured live client; the default is off.
`TYPESAFE_API_KEY` is server-side only. Before a request, the application walks current
input dependencies and requires `send_to_provider` on each source rights grant. Learning
a phrase profile is not permission to send the underlying material to a remote service.
The same check runs before cache reuse so revoked/expired material cannot bypass policy.

Requests are limited by byte count, question count, batch count, timeout and attempts.
These are explicit engineering budgets, not a claim that bytes equal provider tokens.
The provider's returned usage is retained where valid. Unknown usage after a failed call
is unknown cost exposure, not zero cost. Pricing is a user-supplied input to the cost
estimator; the release does not hard-code a lasting commercial promise.

### 26.4 Capture before interpretation

For each attempt, response bytes, HTTP status, truncation flag, request metadata,
checksums and capture time are committed to `provider_receipts` before JSON decoding,
schema validation or semantic use. Authentication headers are not included. A transport
failure has an explicit empty-body receipt. Capture failure stops processing; the code
does not proceed with an unrecorded semantic decision.

Private request metadata contains the actual supplied state and may be sensitive.
Receipts belong in the private workspace, are covered by backup/retention policy and
must not be exposed through a public static directory. `verify_provider_receipts` checks
stored byte hashes. Hash consistency is not an independent witness against an
administrator who can rewrite the entire database and audit chain.

### 26.5 Contract validation and quantization

JSON duplicate keys and non-finite literals are rejected. Numeric values cannot be
Booleans, strings, infinities or out-of-range probabilities. Question IDs, answer types,
choice options, score legends, usage fields and resolved model must match the request.
Truncated responses cannot become available decisions. Captured request metadata is
checked against the stored decision bindings and state hash.

The adapter preserves raw Choice/Score distributions and reported scores. It does not
recompute the provider's confidence or demand exact equality between an independently
rounded score and an expectation calculated from rounded probabilities. Narrow
provider-scoped two-decimal compatibility bounds produce explicit warnings; large or
incompatible residuals produce an unavailable result. Values are not silently normalized.
Tests cover this distinction so arithmetic fixture assumptions cannot discard useful
provider evidence without explanation. Noul outputs have their own direct range check.

### 26.6 Fault semantics and retry policy

The outcome is either available or unavailable, with an explicit error code. An
unavailable decision has no semantic answers. Missing credentials, timeouts, model drift,
unknown labels, malformed JSON and incomplete answer maps never become a zero-valued
speaker signal or a "different claim" answer.

Retries are bounded and limited to transport/transient HTTP conditions, including rate
limit and overload responses. Retry-After is honored within the configured maximum.
Schema failures are not retried as network faults. Each attempt receives its own capture;
repeated attempts may incur cost. After a failure the application preserves deterministic
work and routes localization to complete audio inspection. There is no fabricated model
fallback presented as a successful evaluation.

### 26.7 Revision- and rights-aware caching

The cache key includes purpose, state, questions, version, input IDs/revisions, official
endpoint, requested model and validator version. Reuse requires an available decision,
a pinned model, unexpired TTL and current dependencies/permissions. Changing the profile,
transcript, proposition, scope, questions or rights invalidates applicability. The cache
is an optimization over canonical records, not the system of record for truth.

All cache-hit responses preserve the original decision ID and receipt history. Changing
the cache TTL does not rewrite a past model response. Source text is untrusted: instructions
embedded in captions or quotations have no permission to change destinations, reveal
credentials, approve findings or trigger unrelated tool calls.

### 26.8 Release evidence

The included automated tests exercise the HTTP boundary with mocked responses, retries,
raw capture, numerical edge cases, permission rejection, input changes and failure
fallback. No paid live-provider benchmark was run for this release. The adapter must be
verified with authorized real payloads before its signals are used to reduce production
processing. See [confidence documentation](https://docs.typesafe.ai/confidence) for the
provider's terminology; local calibration remains a separate acceptance task.
