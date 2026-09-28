## 21. Optional integrations without project coupling

### 21.1 Ports, not inherited infrastructure

The target defines optional ports for source discovery, source acquisition, speech-to-text,
diarization, source/context retrieval, candidate-claim extraction, prior-review matching,
notification delivery, and publication export. An adapter implements one port through
its own configuration and tests. None may assume another application's database schema,
identity namespace, graph structure, deployment network, or private repository exists.
A local no-provider configuration must continue to run the reference ledger.

The generic retrieval request includes workspace scope, query, permitted source IDs,
record/revision filters, time/scope constraints, result limit, and desired evidence kinds.
The response includes candidate canonical record IDs, source revisions, locators, excerpts,
retrieval method, and limitations. The ledger rechecks visibility and currentness before
using those candidates. Retrieval relevance is not factual support or semantic equivalence.

### 21.2 Model and speech contracts

A speech port receives an authorized asset reference, local/object-store handle provided
outside model text, range/timebase, language hints, preprocessing configuration, and a
model profile. It returns transcript/diarization candidates with input hash, engine/model
version, segments/words, local labels, timing precision, and warnings. It does not return
confirmed real-person identities without a separate reviewed mapping record.

A claim-extraction port receives exact source utterances and context and returns proposals
with grounded spans, speech acts, scope hypotheses, unresolved fields, and model provenance.
An evidence-research port returns cited candidate evidence and analysis of compatibility.
Neither port can write a completed review, alter access rights, or publish. The application
validates returned IDs and limits before storing proposals.

### 21.3 Export contract

A private research export contains record types, stable IDs, revisions, parent references,
source provenance, exact text when permitted, timebase information, scope, reviewed findings,
limitations, and correction/coverage metadata. A consumer must not turn an external review
or candidate attribution into an approved internal finding. A public export is a separately
approved snapshot with explicit content permissions and withdrawal support. The current
JSON export is a private operator backup, not a publication-ready external API product.

### 21.4 Future authorization of integrations

Before enabling an external adapter, record its contract, data sent, secrets location,
allowed operations, provider retention terms, failure behavior, costs, version policy,
and evaluation evidence. Test it in an isolated workspace. Removal of the adapter must
not make canonical source records unreadable. If the owner later authorizes interoperability
with another product, implement a new explicit adapter and mapping specification instead
of silently grafting that product's schema into this repository.
