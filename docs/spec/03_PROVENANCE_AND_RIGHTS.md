## 03. Acquisition, provenance, and rights

### 03.1 Discovery and acquisition are separate operations

A search result may identify a recording without providing authorized bytes. The
acquisition stage accepts only approved source operations: a permitted archive file,
a publisher export, a licensed vendor delivery, owner-supplied media, or another
explicitly reviewed path. A content URL is evidence of location, not permission.
For unavailable media, preserve a reference and access state. Do not produce fabricated
clips, transcripts, or timestamps to compensate for an inaccessible source.

The reference network clients retrieve structured metadata/search responses only.
The media utilities operate on explicit local files. There is no general-purpose
YouTube downloader, arbitrary-URL media fetcher, or credentials-bypassing scraper.
A future acquisition worker must be separately sandboxed and permitted per source.

### 03.2 Rights-grant contract

An approved grant states the source, basis, supporting reference, reviewer, expiry if
applicable, and allowed operations. Operations are distinct: discovery, text storage,
media storage, audio processing, clip derivation, excerpt publication, media publication,
sending to a provider, and external indexing. The absence of an operation means it is
not allowed. An empty grant can be stored as a draft configuration but authorizes no
processing. A grant for one source cannot authorize another source automatically.

The target model adds asset/collection scope, jurisdiction, contractual volume limits,
retention deadline, model-training restrictions, subprocessor restrictions, permitted
publication destinations, and termination handling. v0.1 grants are source-scoped and
operator-attested. They are not a legal-permission verifier. An operator must ensure
the stated scope applies to the actual material. Commercial use or redistribution
questions require reviewing the applicable agreement, not extrapolating from this code.

### 03.3 Provenance layers

A source response has a retrieval timestamp, request identity without secrets, source
URL, source-native ID, transport status, and original bytes when retention is permitted.
A parser output has an input artifact hash, parser version, field mapping, normalized
payload hash, source-record locator, and any warnings. A transcript has the input asset,
engine/model information, language, timing precision, and revision. A speaking-turn
mapping has the supporting identity evidence and reviewer. A review has the precise
proposition, occurrence and evidence revisions it relied on.

The reference `Observation.raw_sha256` hashes canonical JSON, while `ingest_file` retains
and hashes the original input file bytes. These hashes answer different questions.
The target receipt store must link every output observation to its raw artifact and
record position. In v0.1 the CLI returns that file receipt, while the raw observation
contains its native payload; automatic receipt-to-observation indexing is a backlog item.

### 03.4 Four different clocks must not collapse

At minimum preserve event time, upload/publication time, provider-index/first-seen time,
and retrieval time. Review time is another independent clock. A 2026 upload can contain
a 2018 interview. GDELT's `date` is an observed-source timestamp, not proof of when the
speaker spoke. Quotebank's aggregated date describes an earliest article occurrence,
not an original recording date. An archive's generic `date` needs source-specific
interpretation. Unknown event time remains unknown, with optional date precision and
supporting evidence when a reviewer resolves it.

In v0.1 event dates require declared precision and a rationale, but a full temporal
hypothesis object is not implemented. Source dates that cannot safely be called
publication dates remain in raw payloads. Never fill missing event time from upload
metadata simply to make sorting easier.

### 03.5 Revisions and source disappearance

Raw objects are content-addressed and not overwritten by parser revisions. If a source
changes, preserve the old source revision and record a new one. If access expires or
content disappears, retain only material still allowed under the applicable policy.
A source tombstone records availability changes without pretending a withdrawn document
never existed. Public links and excerpts must be withdrawn when required, while the
minimum permitted audit trail is maintained. Automated retention/tombstone processing
is specified but not shipped in v0.1.

The application checks whether referenced grants are expired when writing dependent
records and when building eligible assertion views. Expiry does not automatically erase
stored files in the reference implementation. Production use requires the retention
worker and an audited deletion/withdrawal policy before ingesting restricted collections.

### 03.6 Integrity is not authenticity

The revision store's hashes and audit chain detect inconsistent changes under the
application's threat model. They do not prove a recording is genuine, establish that a
speaker said something, prove the date of acquisition, or resist an administrator who
rewrites the whole database and hash chain. A production deployment may checkpoint
signed manifests externally and use immutable object retention where appropriate.
Source authenticity, legal access, speaker identity, and byte integrity remain distinct
claims with distinct evidence.
