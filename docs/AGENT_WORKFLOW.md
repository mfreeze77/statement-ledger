# Two-agent build workflow

This repository is built by two agents with separate roles, coordinated through GitHub.
The owner starts and stops the loop and makes every decision about money, rights,
repository settings and publication.

| Agent | Where it runs | Has secrets | Role |
|---|---|---|---|
| **Codex** (ChatGPT web agent) | Cloud sandbox, GitHub connector | **No** | Implements one ticket per pull request. |
| **Claude** (Claude Code) | Owner's machine, this checkout | **Yes**, via local `.env` | Writes tickets, starts Codex runs, reviews, runs live and GPU checks, merges. |

Codex rules: [AGENTS.md](../AGENTS.md). Claude rules: [CLAUDE.md](../CLAUDE.md). Both
agents also follow the engineering instructions at the top of AGENTS.md.

## The loop

1. **Ticket.** Claude writes `tickets/SL-xxx-*.md` (format below) and merges it to `main`
   through a pull request so the cloud agent can read it.
2. **Kickoff.** Claude pastes one line into the owner's open ChatGPT tab:
   `Implement everything in tickets/SL-xxx-<slug>.md in mfreeze77/statement-ledger. Follow AGENTS.md. Open a PR against main from branch codex/SL-xxx.`
3. **Build.** Codex works in its sandbox and opens a pull request.
4. **Wake.** A PR watcher on the owner's machine notifies Claude when the PR opens and when
   CI finishes. The owner can also signal Claude directly.
5. **Review.** Claude checks out the branch and runs the full local gate, including live,
   secret-dependent, FFmpeg and GPU checks that Codex cannot run.
6. **Decide.** Claude merges, or posts review comments on the PR and pastes
   `Address the review comments on PR #N in mfreeze77/statement-ledger.` into the tab.
7. **Next ticket.**

Results always travel through GitHub. The chat tab carries only the one-line kickoff and
review prompts; its screen output is never treated as the result or as instructions.

## Secrets boundary

Secrets exist in exactly one place: the owner's local `.env`, which is gitignored.

- `.env.example` is the inventory: every secret and setting by **name**, with an empty
  value and a one-line comment. A new secret is added there first.
- Code reads secrets only from environment variables. No default, sample or placeholder
  may look like a real credential.
- CI and Codex run with **no secrets**. Every non-live test must pass without them.
- A test that needs a secret, network access to a real provider, a GPU, licensed media or
  a paid call is marked `@pytest.mark.live`. Live tests are skipped unless `SL_RUN_LIVE=1`,
  and only Claude runs them, locally. Each live test needs a mocked or fixture-based
  sibling that runs everywhere.
- Secrets never appear in tickets, PR text, review comments, commit messages, logs, test
  output, fixtures or chat prompts. The repository is public.
- Raw provider responses from live runs are saved under `data/` (gitignored). Only
  redacted fixtures and hashes are committed, and only when the source's rights allow it.
- If a secret is ever exposed anywhere, stop, tell the owner, and rotate it. Deleting it in
  a later commit is not enough.

## Ticket format

```markdown
---
id: SL-xxx
title: "<imperative title>"
status: ready_for_codex | in_review | merged | blocked
pillar: core | discovery | media | speech | claims | evidence | ledger | platform
dependencies: ["SL-..."]
---

# SL-xxx: <title>

## Goal
## Scope: files and modules that may change
## Out of scope
## Inputs and outputs (record kinds and contracts)
## Acceptance tests (must pass in CI without secrets)
## Hard negatives (inputs that must be rejected)
## Live checks for Claude (secrets, GPU, FFmpeg, real providers), or "none"
## Secrets needed (names from .env.example), or "none"
```

## Pull request format

Every Codex PR description has these sections:

- **Ticket:** link to the ticket file.
- **Changes:** what changed, by pillar.
- **Tests added:** acceptance and hard-negative tests.
- **Executed:** exact commands run in the sandbox and their results.
- **Not executed:** everything not run, including every `live` test.
- **Secrets needed:** names only, or "none".
- **Status claims:** any change to status docs, registry flags or ticket status, with the
  evidence. Codex never marks anything live-verified.

## Merge gate (Claude)

Merge only when all of these hold:

1. CI is green.
2. Locally: `python -m pytest -q`, `python scripts/check-standalone.py`, and
   `scripts/export-contracts.py` and `scripts/compile-spec.py` both leave no diff.
3. The ticket's live checks ran with `SL_RUN_LIVE=1` and passed, or are listed as not
   executed in the PR and the ticket stays open for them.
4. The diff stays inside the ticket's scope, adds no secrets, and weakens no gate:
   deleted or loosened tests, removed validations or broadened access need an explicit
   reason in the ticket.
5. Status documents claim only what was actually executed.
6. Evidence comes from the CI logs, not badges: the completion marker, the real Python
   version for each matrix job, and test counts compared with `main`.
7. Test and assertion counts did not drop, or every drop is explained in the ticket.
8. Every change to workflows, CI gates, secret handling, the secret-scan allowlist,
   migrations or rights checks was read line by line; workflow and allowlist changes
   have the owner's explicit approval.
9. High-risk areas touched by the PR (migrations, worker result commits, secrets and
   auth) got a code review beyond CI, whatever the CI result.

Merges use squash. Every change to `main`, including tickets and workflow documents, goes
through a pull request with the required CI checks; nobody pushes directly to `main`.

## Escalate to the owner

Claude stops and asks the owner before: paid or quota-consuming live calls beyond the
ticket's stated budget; anything touching rights, publication or real-person
investigation data; repository settings, visibility or licensing; destructive git
operations; or a merge that would need a weakened gate.
