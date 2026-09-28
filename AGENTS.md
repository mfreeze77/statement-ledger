# Engineering instructions

Treat this repository as a completely independent application. Do not read from,
write to, import from, migrate from, or make runtime assumptions about another
private application unless the owner explicitly authorizes a future integration.

Read SPECIFICATION.md, docs/IMPLEMENTATION_STATUS.md, and the chosen ticket first.
Also read docs/runbooks/FOUNDATION.md and the owning module README; do not expand the source/spec backlog as foundation work.
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

## Rules for Codex (cloud agent)

You implement tickets. The full loop is in [docs/AGENT_WORKFLOW.md](docs/AGENT_WORKFLOW.md).

- Work from one ticket file per run. Use one branch named `codex/SL-xxx` and open one pull
  request against `main`. Never push to `main`, merge your own PR, force-push, or rewrite
  history.
- Change only what the ticket's scope lists. If the ticket is wrong or blocked, say so in
  the PR instead of widening scope.
- You have no secrets, and you must not need them. Never ask for, invent, hard-code or
  commit a credential, token or realistic-looking placeholder. Refer to secrets only by
  their names in `.env.example`; add any new secret there with an empty value.
- Mark any test that needs a secret, a real provider, a GPU, licensed media or a paid call
  with `@pytest.mark.live`, and give it a mocked or fixture-based sibling. Live tests are
  skipped unless `SL_RUN_LIVE=1`; the local agent runs them.
- Before opening the PR, run `python -m pytest -q`, `python scripts/check-standalone.py`,
  `python scripts/export-contracts.py` and `python scripts/compile-spec.py`, and commit any
  regenerated contracts or specification.
- Write the PR description in the format in docs/AGENT_WORKFLOW.md, including an honest
  "Not executed" section. Never set `live_connection_verified`, mark a model or source as
  live-verified, or upgrade an implementation status without executed evidence.
- Review comments on your PR are your next instructions; push fixes to the same branch.
- Do not edit AGENTS.md, CLAUDE.md or docs/AGENT_WORKFLOW.md unless the ticket says so.
- Deliver code only as plain, reviewable commits. Never commit encoded, compressed or
  split payloads that are unpacked later, and never add a workflow that writes to the
  repository. If you are blocked from pushing, say so in the PR instead of working around it.
- Changes under `.github/workflows/`, to CI gates, the secret-scan configuration or any
  allowlist must be called out in the PR description; they need the owner's explicit
  approval before merge.
- A passing check counts only if its log proves it: every check step must fail the job
  on failure (no unguarded pipes, `|| true` or `continue-on-error`), and CI prints a
  completion marker plus the real interpreter version and test counts.
