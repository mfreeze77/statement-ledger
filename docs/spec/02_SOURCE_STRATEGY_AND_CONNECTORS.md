## 02. Source strategy, registry, and connector contract

### 02.1 Every discovered source remains represented

The source registry covers YouTube; CNN and CBS transcripts; Internet Archive; GDELT
Television Explorer, Visual Explorer, television ngrams, and Global Quotation Graph;
Quotebank; Media Cloud; LexisNexis/Nexis Uni; TVEyes; Critical Mention; Sprinklr;
SnapStream; Grabien; AAPB; C-SPAN; Vanderbilt; Google Fact Check Tools; ClaimReview;
Fact-Check Insights; MediaVault/MediaReview; PolitiFact; PunditFact; FactCheck.org;
Reuters Fact Check; AFP Fact Check; Media Matters; Media Research Center; NewsBusters;
NewsGuard; and Full Fact AI. Authorized manual input supplies a common pathway for
sources whose dedicated transport or format has not yet been verified.

The registry also covers the Internet Archive TV News Archive's caption search, which is
distinct from the general Internet Archive metadata interface and underlies GDELT
Television Explorer; a segment found through both is one lead, not two. Statements the
subject publishes directly are first-party inputs: subject-operated social media accounts,
bylined columns, op-eds and newsletters, and podcast and radio appearances. The subject's
own video channel is collected through the YouTube source. First-party publication still
requires reviewed account ownership or bylines; an impersonation account, a reposted
item, or a publisher-written headline is not the subject's assertion.

A separate `primary_evidence` role holds sources used to check a proposition rather than
to find statements: Congress.gov, GovInfo, the Federal Register, the Bureau of Labor
Statistics, the Census Bureau, FRED, OpenFEC, CourtListener, and a catch-all for other
official publications entered through the manual envelope. These are queried from an
extracted proposition's scope (date, geography, quantity, definition, document version),
never from the subject's name, and the person planner marks them `claim_driven`. A
retrieved record bears on a proposition; it is not a finding. Retrieval, snapshotting and
exact locators are specified by SL-014.

These are not equivalent products. ClaimReview is a vocabulary. AAPB is an archive.
Full Fact AI is a workflow product. Some sources produce citations, some provide
metadata, some permit transcript delivery, and some provide licensed content only.
Their roles cannot be inferred from a count of names in the registry.

### 02.2 Registry fields

Each entry has a stable source ID, human-readable name, role, access class, implementation
class, parser key or null, documentation URLs, known limitations, next integration step,
review date, default enabled state, and live-verification state. All connectors are
disabled by default. Production extensions add contract version, allowed hostnames,
authentication profile reference, supported languages, coverage intervals, source-date
semantics, retention rules, cost unit, and supported discovery/acquisition operations.
Secrets are never stored in a registry object. Schema versions and legal permissions are
separate: a valid response shape does not grant storage or redistribution rights.

### 02.3 Required input envelope

The common source envelope records `source_id`, `native_id`, source URL, source-provided
title, observation kind, optional quoted/transcript text, reported speaker if any,
publication date only when its meaning is known, discovery links, raw payload, payload
hash, parser version, retrieval time, and rights-grant reference. The raw file archive
also records a byte-level SHA-256. A normalized-payload hash is not a substitute for the
hash of the original compressed file. Both serve different reproducibility needs.

The contract accepts observation kinds such as appearance lead, quotation lead, external
review, media review, transcript lead, frequency signal, metadata, and primary document.
No parser may emit a confirmed person-to-voice mapping, accepted utterance, or completed
internal review merely because an upstream record uses a speaker name or verdict label.

### 02.4 Transport behavior

A network connector has explicit authentication, endpoint, timeout, retry, pagination,
size, and budget boundaries. It preserves the input cursor and next cursor. A retry must
not double-count a successful page. Repeated cursors and inconsistent request identities
stop the run for inspection. Authorization errors are not retried blindly. Quota and
transient errors use a bounded delay. Error messages must not include credential-bearing
URLs or upstream bodies. Redirect behavior is explicit. The v0.1 JSON clients use fixed
HTTPS origins, reject redirects, cap decompressed response bytes, and do not fetch URLs
found inside results.

YouTube's official documentation describes paginated search and notes incomplete/index-
dependent results; channel uploads can be inspected through upload playlists. Caption
download has a different authorization requirement. Discovery metadata is therefore not
an implicit media-acquisition channel. References: [YouTube search](https://developers.google.com/youtube/v3/docs/search/list),
[caption download](https://developers.google.com/youtube/v3/docs/captions/download),
and [developer policies](https://developers.google.com/youtube/terms/developer-policies).

### 02.5 File parsing behavior

File parsers support bounded line-delimited UTF-8 records, gzip and bzip2 compression,
source-native JSON, explicit field validation, and error receipts. Large JSONL inputs
are streamed rather than loaded into memory. Root arrays in v0.1 are limited to 64 MiB
decompressed; larger arrays need a streaming converter or a future array-streaming
adapter. A record limit is a workload boundary, not evidence of corpus completion.
Malformed rows are retained through the source archive and reported with location.
Schema drift must be quarantined, not silently interpreted as an empty successful run.

GDELT documents per-minute compressed JSONL with nested quotations and surrounding
snippets. Quotebank documents both aggregated quotation-centric and article-centric
representations. v0.1 supports the quotation-centric variant only. Their source dates
are not automatically converted into event or publication dates. References:
[GDELT GQG](https://blog.gdeltproject.org/announcing-the-global-quotation-graph/),
[Quotebank schema](https://zenodo.org/records/4277311).

### 02.6 Commercial and publisher connectors

For a commercial source, obtain an actual sample export, endpoint specification,
retention/derivation rights, authentication method, stable record identifiers, timebase,
coverage statement, and backfill limits before implementation. A generic guessed REST
adapter is not an acceptable substitute. For publisher HTML, prefer authorized exports
or structured records; use robust parsing only after permission and samples are recorded.
Manual input must retain the actual source ID, not disguise all material as user-created.
The source-specific worksheets and source matrix define the next action for each entry.
