## 15. Security, privacy, and deployment constraints

### 15.1 Threat model

Untrusted inputs include source URLs, API responses, compressed corpora, HTML/transcripts,
media containers, external review text, model output, signed source links, and uploaded
configuration. Threats include server-side request forgery, local-file access, malicious
media decoders, decompression exhaustion, cross-site scripting, prompt injection,
credential leakage, cross-workspace access, forged identity mappings, source poisoning,
duplicate inflation, race conditions, and stale or unauthorized publication.

The project also treats evidentiary errors as integrity failures. A valid login does not
make a statement attribution correct. A checksum does not make a quote authentic.
Security controls, provenance checks, and factual review are complementary, not
interchangeable.

### 15.2 Reference security posture

The reference API is intended for a private local single-owner workspace. All data routes
require a bearer token. HTTP write bodies are bounded; source clients cap responses,
reject redirects, use fixed endpoints, and suppress credential-bearing error details.
The browser renders untrusted content as text and does not persist the token. Media
utilities use an explicit local root, fixed command arguments, and no shell interpolation.
SQLite queries use parameter binding. External source links are not automatically fetched.

The Docker configuration uses a non-root process, loopback-bound host port, read-only
application filesystem, a dedicated data volume, dropped capabilities, and no-new-
privileges. It does not claim a production security audit, multi-tenant isolation, rate
limiting, TLS termination, centralized secret storage, full decoder sandboxing, or a
complete public-service defense. Docker execution itself must be validated on the target
host. No public deployment is authorized by passing the unit tests.

### 15.3 Production identity and authorization

The target system uses actual authenticated principals and server-side roles for owner,
source operator, researcher, reviewer, publisher, and read-only auditor. Roles constrain
operations and source access. Workspace IDs come from authenticated scope, never from an
unchecked client filter. Every endpoint, export, object-store link, search query, and
background job is bound to the authorized workspace and source grants. Audit actor IDs
are server-controlled. The client cannot approve its own role by setting reviewer text.

Database row-level controls and application authorization are tested independently.
Foreign record IDs, stale sessions, object-store keys, job IDs, and cached search results
must not leak data across workspaces. The target deployment should support separate
physical workspaces where rights or customer isolation make that simpler than shared
multi-tenancy. No other project's identity provider or tenant table is assumed.

### 15.4 Network and media isolation

A future general source fetcher needs hostname/scheme allowlists, DNS/IP validation,
redirect revalidation, private-network and metadata-service denial, response/time limits,
and controlled egress. Signed URLs and authentication query parameters must not appear
in model contexts or public logs. The source URL retained for provenance may need a
redacted public variant and a restricted acquisition reference.

Media workers should not have database-owner credentials or unrestricted outbound
networking. A job receives a validated local object and outputs a derivative plus a
manifest. Resource limits cover memory, CPU/GPU, wall time, disk, subprocess count, and
output expansion. Source media is read-only. Malformed decoders fail the job, preserve
a safe error code, and do not terminate the queue or reinterpret missing words.

### 15.5 Retention and privacy

Retain only what the collection purpose and source agreement allow. Rights include
provider transfer and indexing, not just downloading. Credentials live outside Git and
outside source manifests. Biometric reference features, when separately approved, are
restricted and minimized. Do not collect private communications or infer protected or
sensitive personal attributes as part of public-statement analysis. Removal requests,
source access changes, and verified attribution errors require auditable handling.

The reference implementation checks grant expiry for new dependent work and currentness,
but it does not automatically purge raw files. A retention worker, deletion proof,
publication withdrawal, backup retention policy, and testable restore implications are
mandatory before restricted real-world collections are used in production.

### 15.6 Supply chain and release checks

Keep direct dependencies explicit and record the tested runtime. Generate an environment
manifest and a resolved dependency lock in a network-enabled environment; do not fabricate
a hash lock when dependency resolution failed. Optional GPU/model dependencies belong
in separate worker images with recorded license/model access and pinned revisions.
CI must check tests, generated contracts, namespace independence, dependency audit,
secrets, and relevant source/model integration gates. Unit tests are necessary but do
not replace live permission checks, deployment inspection, or an adversarial review.
