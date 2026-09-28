# Engineering instructions

Treat this repository as a completely independent application. Do not read from,
write to, import from, migrate from, or make runtime assumptions about another
private application unless the owner explicitly authorizes a future integration.

Read docs/runbooks/FOUNDATION.md, docs/IMPLEMENTATION_STATUS.md, the owning module README, and the chosen task first. Load only relevant product-spec sections; do not expand the source/spec backlog as foundation work.
Actual code and test evidence define implementation status. Never mark a vendor
connected because its name appears in the source registry. Never claim a model
worked merely because a fixture or mocked HTTP response passed.

Preserve original source records, source dates, speaker uncertainty, exact text,
record revisions, rights constraints, and provenance. A semantic match creates a
candidate, not a merged proposition or reused review. Never use party, ideology,
network reputation, or personal preference as truth evidence. Do not fabricate
statements or findings about real people in fixtures.

Changes to foundational evidence invalidate downstream findings. Tests must cover
hard negatives as well as happy paths. Run pytest, schema regeneration/diff, the
standalone guard, and relevant integration checks. State what was not executed.
Do not weaken a gate or broaden access to turn a failed test green. No credentials,
licensed media, source corpora, model weights, or user database in Git.

## Acceleration-specific invariants

Only accepted, current, permissioned turns train speaker profiles. Original events, not
reposts, are the unit of feature support. Never train from a profile's own candidates.
Shadow mode defaults to all audio; low-scoring windows remain unprocessed, not absent.
Scope compatibility must preserve negation, date, geography, quantity and definitions.
Jev scores are uncalibrated routing features; backend failure cannot become no/false.
Capture provider bytes before validation; fixed endpoint and source egress grants apply.
Keep every claim card current against its reviews, source rights, expiry and corrections.
Run regression tests for migrations, cache invalidation and end-to-end selective media.

## Executable foundation rules

Run `make check` (PowerShell: `./scripts/dev.ps1 check`) and `make proof` before delivery.
Native equivalent: `uv sync --locked --group dev`; `uv run --locked python scripts/check.py check`.
Run focused tests through the same uv environment. Never silently update uv.lock; dependency
changes require an explicit `uv lock` and a reviewed diff. GPU dependencies have a separate
lock/environment and do not belong in the API. CPU checks do not prove GPU inference.

Core owns synchronous invalidation, revisions, rights and transactions. Pillars do not
import siblings or root legacy facades. Application is the explicit composition root.
Every writable record kind has exactly one registered validator; missing registrations
fail startup. New features go in the owning package, not compatibility wrappers.

Runtime startup only checks migrations. Do not edit applied SQL/checksums or rewrite old
record hashes. Back up first and prove restore. Do not run models, FFmpeg or downloads
inside a database transaction. Workers prepare proposals; only a fenced commit can attach
results after rechecking input versions and rights. Register artifacts before enqueue.
Unconfirmed identities and model guesses remain unconfirmed. No new publication authority.

Only named secret references belong in the registry. Never print or commit credentials,
raw provider bodies, real assets, models or databases. Costs can be unknown; never convert
an ambiguous remote attempt into a free successful retry. Repository settings, licensing,
personal Git identity and history are owner decisions, not coding-agent cleanup.
