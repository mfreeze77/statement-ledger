## 12. API, commands, event contracts, and concurrency

### 12.1 Implemented operator API

The reference API requires a bearer token for all data, schema, plan, and integrity
endpoints. The static shell and minimal health response are public within the local
server. The token is injected from `SL_API_TOKEN`, must be at least 32 characters, and
maps to the single-owner actor. Reviewer text in a record is separate from the request
actor. The server does not offer a public account-registration flow.

| Method and path | Implemented behavior |
|---|---|
| `GET /healthz` | Service/version/mode only |
| `GET /api/sources` | Packaged connector registry |
| `GET /api/counts` | Record totals by kind, not person assessments |
| `GET /api/schema/{kind}` | Generated record payload schema |
| `GET /api/records/{kind}` | Bounded record list with offset/limit |
| `GET /api/records/{kind}/{id}` | Current or explicitly requested historical revision |
| `GET /api/history/{kind}/{id}` | Revision history |
| `POST /api/records/{kind}` | Validated append/update with expected revision |
| `GET /api/people/{id}/ledger` | Eligible assertions, evidence/reviews, exclusions, coverage |
| `POST /api/discovery/plan` | Non-executing source plan |
| `POST /api/scope/compare` | Candidate compatibility; never automatic review reuse |
| `POST /api/clips/plan` | Bounded source/context intervals; no media download |
| `GET /api/integrity` | Audit and record-hash consistency checks |
| `GET /api/openapi.json` | Authenticated OpenAPI contract |

A record write body contains `record` and `expected_revision`. Creating a new record
uses expected revision zero. Updating requires the current head revision. A conflict
returns HTTP 409. Missing references return 404 and invalid payloads/invariants return
422. Oversized write requests exceed a 4 MiB bound and return 413. The code stores a
trusted request actor rather than accepting an arbitrary actor header.

### 12.2 Idempotence versus concurrency

An exact retry with the correct expected revision may return the existing record without
creating another revision. A stale expected revision is still a conflict, even if the
request resembles an old payload. Do not let generic upsert semantics overwrite a newer
review. Imports use stable source IDs and compare normalized content so unchanged
source records do not create repeated revisions merely because retrieval time changed.
A changed source payload creates a new revision using the current expected head.

Stable observation IDs are source-scoped; IDs do not prove two sources refer to the same
underlying investigation. Canonical linking requires an explicit relation or reviewed
equivalence. Cross-source raw record collisions must not overwrite material. Content
hashes and source-native IDs both need to be retained because neither alone answers all
deduplication questions.

### 12.3 CLI as the reference workflow surface

The CLI supports source listing, deterministic planning, name-only subject seeding,
synthetic demo seeding, record get/put, person-ledger projection, file ingestion, timed-text
or ASR-export import, explicit paginated source discovery, local clip derivation, optional
speech processing, integrity checks, native SQLite backup, private JSON export, and schema
export. Commands that require paid or authenticated providers do not run automatically.
Source credentials are environment configuration, not model arguments or repository files.

The CLI's `discover` command writes raw responses and a pagination receipt; it does not
promote results to appearances. `ingest` requires an explicit source and rights grant.
`import-transcript` requires a known asset. Local media commands verify the registered
asset checksum before processing. This sequence makes permission and lineage visible
instead of hiding several unrelated operations behind one ambiguous "analyze person" call.

### 12.4 Target task and event envelopes

The production task envelope contains task ID, investigation ID/revision, source/operation,
input record IDs/revisions, idempotency key, cursor, budget reservation, rights snapshot,
worker class, attempt, lease token/expiry, deadline, and output schema version. A result
contains outputs, next cursor, bytes/time/tokens used, completion meaning, errors, and
source receipts. Secret values never appear in either envelope.

The reference store emits `record.created` and `record.revised` outbox entries in the
same transaction as the record. Target event types add discovery.page_received,
asset.acquired, transcript.produced, attribution.reviewed, utterance.accepted,
claim.proposed, evidence.revised, review.completed, dependencies.invalidated,
correction.opened/resolved, publication.withdrawn, and retention.completed. Consumers
must be idempotent and track processed event IDs; an outbox row is not proof a downstream
effect occurred. Outbox consumption and delivery acknowledgements are not implemented
in v0.1.

### 12.5 Compatibility and contract testing

Generated JSON Schemas and OpenAPI snapshots are version-controlled. CI regenerates them
and fails on unexplained drift. New record fields require migration/backward-compatibility
review. Unknown fields are rejected rather than silently ignored. Provider adapters have
recorded source fixtures and explicit parser versions. A commercial vendor contract must
be based on an actual supplied schema, not an invented endpoint that happens to look
plausible. Contract tests prove known shapes, not provider access or real-world accuracy.
