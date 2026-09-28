## 22. Reference limitations, unresolved decisions, and next gate

### 22.1 Implemented does not mean production-complete

The reference implementation provides a concrete storage/API/CLI/inspection workflow,
source-shaped parsing, bounded metadata clients, local media utilities, optional speech
calls, and synthetic correctness tests. It is useful for inspecting source formats,
prototyping the investigation chain, testing provenance rules, and developing later
workers. It is not a complete autonomous crawler, a reviewed real-person corpus, a
public fact-checking publisher, or a multi-user production deployment.

Exact-coordinate duplicate grouping does not solve near-duplicate alignment. Reviewer
strings are single-owner attestations rather than independently authenticated reviewer
roles. Root-array JSON import is bounded rather than a fully streaming array parser.
The raw-file receipt is returned but not fully indexed as its own canonical record.
The queue library is not wired into a scheduler/outbox executor. The operator UI lacks
waveform editing, synchronized transcript playback, and full review forms. Retention,
public withdrawal, prediction outcomes, production RLS, and live provider QA are planned.

### 22.2 External validation still required

Source network smoke requests for a GDELT sample and AAPB metadata failed because the build
runtime could not resolve hostnames. Official documentation was reviewed through web
access, but this does not constitute successful programmatic integration from the runtime.
YouTube and Google Fact Check clients require owner-supplied credentials. Commercial
providers require actual access contracts. Optional speech models were not downloaded or
run. Docker and clean dependency resolution require a network-enabled target environment.
A resolved cross-platform hash lock must not be invented; the package records its tested
local versions and leaves a lock-generation gate explicit.

### 22.3 Questions resolved by defaults

The initial repository is private by default when published with the supplied script.
There is one owner workspace and no public publishing. All source connectors are disabled
until explicitly invoked/configured. The subject example has no inferred aliases, current
role, channel IDs, findings, or automatically authorized spend. Source rights start empty
unless the operator supplies a documented grant. The demo uses fictional data. These
choices allow work to proceed without silently assuming decisions that affect privacy,
rights, cost, or factual integrity.

### 22.4 Decisions for the next authorized pilot

Select the actual date window and source subset, confirm the subject identity references,
obtain a permitted original/copy pair, choose and validate the speech worker environment,
and define reviewer acceptance examples. Confirm retention and provider-transfer rights
before processing restricted material. Measure real schema shapes, audio quality, and
review effort. Use that evidence to prioritize the next tickets instead of treating the
number of nominal connectors as progress.

The next gate is successful, source-bound ingestion and review of a real authorized
appearance with a documented original/copy relationship. That gate can end with supported,
contradicted, mixed, unresolved, or no checkable claim findings. The required result is
an auditable research process—not a predetermined conclusion about the subject.
