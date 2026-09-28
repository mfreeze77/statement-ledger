## 11. Architecture, storage, and component boundaries

### 11.1 Reference deployment

The shipped system is a modular Python application with a FastAPI operator API, a CLI,
static browser assets, a SQLite revision ledger, optional raw local files, and a durable
job-ledger library. No database server, vector database, message broker, external model,
cloud account, or private application is necessary for the synthetic demo. The source
registry is packaged data. JSON Schemas are generated from Pydantic models. The browser
uses the same authenticated API as command-line clients.

The current component ownership is explicit:

| Module | Responsibility |
|---|---|
| `models.py` | Typed canonical record payloads and local field invariants |
| `service.py` | Cross-record validation, rights/currentness checks, ledger projection |
| `store.py` | Transactional revision storage, heads, dependencies, audit/outbox |
| `connectors/registry.py` | Source inventory and implementation/access status |
| `connectors/parsers.py` | Native source records to observation candidates |
| `connectors/http.py` | Bounded source metadata/search clients |
| `ingest.py` | Retained file archive and revision-aware import receipts |
| `transcripts.py` | Timed text and ASR-export normalization |
| `speech.py` | Optional local ASR/diarization calls and conservative label matching |
| `media.py` | Local clip-range planning and FFmpeg derivation |
| `jobs.py` | Standalone queue records, leases, attempts, and safe completion |
| `api.py` / `cli.py` | Operator entry points; neither is a truth engine |

### 11.2 Canonical source of truth

Record revisions are canonical. Current heads point to a revision and may be stale.
The dependency index records which parent revisions justified a child. Changes to a
parent mark its descendants stale. Audit and outbox entries are committed with the
record revision. Indexes, search embeddings, UI summaries, and analytical groupings
are derived views and must be rebuildable. A model-provider cache cannot become a
second authoritative claim store.

SQLite uses a single-workspace reference schema. The API creates a separate store
connection per request, while write operations use immediate transactions. The code
is not a multi-tenant high-throughput system. A PostgreSQL adapter is planned before
multi-user production use. It must preserve revision identities and dependency semantics;
changing the storage engine must not change the meaning of a claim or count.

### 11.3 Target services and independent scaling

The target architecture has an operator API/UI, discovery planner, source workers,
acquisition workers, isolated media workers, extraction/retrieval workers, review service,
projection service, and retention/publication workers. Initially these may be modules in
one deployable application with explicit process separation for untrusted media. Split
services only when workload or security requirements justify the operational cost.

Metadata discovery is network-bound; audio processing may be CPU/GPU-bound; raw media
storage is capacity-bound; human review is a separate bottleneck. A queue must distinguish
these resource classes. Running an audio job in an HTTP request is not acceptable for the
target deployment. Each worker consumes a versioned input envelope and produces a
versioned result that references its exact inputs. Failures preserve diagnostic states
without marking the underlying claim false or the investigation complete.

### 11.4 Production database design

The PostgreSQL design retains append-only record revisions, current heads, dependency
edges, audit events, and outbox events. Add workspace IDs, principal IDs, row-level access
controls, immutable source artifact manifests, durable task attempts, and explicit
publication snapshots. Typed projection tables accelerate common queries over events,
persons, turns, proposition scopes, occurrence groups, and review states. A projection
has a generation/version and can be rebuilt from canonical revisions.

Database constraints must enforce nonnegative and ordered intervals, referential
integrity, unique source-native keys, expected revision checks, and group membership
integrity. Transactional application validation remains necessary for rich scope/identity
rules; SQL alone does not determine semantic equivalence. Cross-workspace joins are
prohibited unless an explicit shared-source abstraction has reviewed permissions.
Multi-tenancy must be tested using adversarial foreign IDs at every API boundary.

### 11.5 Search and graph capabilities

A minimal local search can use lexical indexes and explicit filters. Semantic retrieval
is an optional candidate-generation port. A graph representation can connect source,
event, asset, utterance, person, proposition, evidence, and review objects, but must not
replace the canonical revision store or bypass source access. Graph expansion returns
provenance paths and supported relations, not unsupported causal assertions. An external
index response must include canonical IDs and source revisions that the ledger can check.

The default standalone build does not connect to any external retrieval service. A
future adapter must conform to the generic retrieval contract and be removable. No
private repository code, namespace, or credentials are embedded in the architecture.

### 11.6 Migration and rollback

Schema changes need explicit migration IDs, a backup before execution, a forward
migration test, compatibility checks against generated contracts, and a rollback or
restore plan. Do not silently regenerate IDs when migrating record kinds. A rollback
must disable new publication/processing first, preserve pending jobs and source receipts,
and avoid acknowledging outbox events whose effects are not durable. A code rollback
that makes new records unreadable is not sufficient; define a data compatibility window
or a validated restore procedure.
