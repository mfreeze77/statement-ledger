# Statement Ledger 0.3.0 — Foundation

**A standalone, source-bound public-statement ledger with reusable research and transcript-first speaker localization.**

```text
33 named media/data sources + TV News Archive + first-party channels
   + authorized manual input; primary-evidence sources for checking claims
   → source observations → original appearances and assets
   → caption windows + confirmed-turn language profiles
   → optional Jev candidate screening → selected audio work
   → reviewed speaker identity → exact utterances and occurrences
   → shared scoped claims → evidence/review cards → corrections
```

This application owns its repository, schema, storage, API, deployment, tests, source registry,
and backlog. No other private application, identity provider, retrieval service, or model
provider is required. The base application and all demonstrations run without model credentials.

## Start here

| Need | Read |
|---|---|
| Complete original and expanded design, 29 chapters | [SPECIFICATION.md](SPECIFICATION.md) |
| Foundation commands, configuration, migrations and jobs | [Operating guide](docs/runbooks/FOUNDATION.md) |
| Phase 0 implementation and validation | [Status](docs/PHASE0_STATUS.md), [evidence](docs/PHASE0_VALIDATION.md) |
| Earlier acceleration changes | [v0.2 release notes](docs/RELEASE_NOTES_V0_2.md) |
| Existing database or v0.1 checkout | [Upgrade runbook](docs/runbooks/UPGRADE_V0_2.md) |
| Tested implementation versus remaining work | [Implementation status](docs/IMPLEMENTATION_STATUS.md) |
| Executed checks and limitations | [Validation report](docs/VALIDATION_REPORT.md) |
| Caption screening and selective audio processing | [Localization runbook](docs/runbooks/SPEAKER_LOCALIZATION.md) |
| Large claim-seed inputs and reusable evidence | [Claim-library runbook](docs/runbooks/CLAIM_LIBRARY.md) |
| Next implementation work | [Ticket index](tickets/INDEX.md), [coding-agent kickoff](KICKOFF_PROMPT.md) |

## What is runnable

The statement-ledger and acceleration features are retained. The foundation release adds explicit migrations, a fenced worker, typed settings/secrets, immutable artifacts, locked environments and modular ownership; it does not automatically connect new sources. Existing product capabilities include:

- **Independent shared claims:** SQLite FTS5 search, topical families, source-bound bulk
  JSONL/gzip/bzip2 seed import, and exact-proposition review cards with scope, expiry,
  correction and revision gates. Imported text creates leads, not findings.
- **Learned language profiles:** opening, closing and recurring n-grams learned from
  accepted target turns versus explicitly selected comparison speakers. Event-level
  counting avoids repost inflation. Refresh incorporates new accepted turns while
  excluding named holdout events; derived guesses never train themselves.
- **Caption-first localization:** overlapping windows, phrase/handoff hints, contextual
  padding, deterministic rejected-window audits, caption-gap coverage, cross-person
  interval union, and explicit full-audio fallback. Shadow mode is the default.
- **Optional TypeSafe Jev adapter:** bounded Noul/Choice/Score contracts, raw-response
  capture before validation, bounded retries, exact model pinning, dependency-aware
  caching, usage receipts, and failures that cannot become negative semantic answers.
- **Selected audio execution:** verify the original asset hash, clip chosen regions with
  FFmpeg, optionally transcribe/diarize, and retain source offsets plus a durable
  success/failure manifest. Speaker labels remain local to each clip.
- **Evaluation:** held-out event checks, target-time and turn coverage, calibration
  diagnostics, and operator-priced cost comparison. These do not automatically promote
  a model, fit a probability calibrator, confirm an identity or publish a finding.
- **Private operator surfaces:** CLI, authenticated API, and added browser views for
  profiles, localization plans and the shared claim library. No frontend dependency build.

There are 20 canonical record kinds, generated schemas/OpenAPI, append-only revisions,
optimistic concurrency, dependency invalidation, audit checks and native SQLite backup.
Existing source clients cover YouTube metadata, Google Fact Check, Archive and AAPB
metadata; their network contracts are tested with mocks. The other sources retain their
access/onboarding worksheets. They are not all live connections.

## Local quick start

Use Docker Compose for the shared development/test environment. No source/model credential is needed for tests.

```bash
make up
make check
make proof
make doctor
make down
```

On Windows, use `./scripts/dev.ps1 up` and `./scripts/dev.ps1 check`. The command runner creates a private ignored local operator token when needed; the API binds only to localhost. Source files are mounted directly; package environments are not shared with the host. Down never deletes data volumes.

Read **[the foundation operating guide](docs/runbooks/FOUNDATION.md)** before using an existing database. Startup does not create or upgrade a schema. `statement-ledger migrate` is explicit; an old default database is detected rather than replaced with an empty one. Numbered migrations preserve prior record hashes and audit history.

For native Python 3.11–3.13 work:

```bash
uv sync --locked --group dev
uv run --locked python scripts/check.py check
uv run --locked statement-ledger --db data/demo-v02.sqlite3 demo-acceleration
```

The demo is explicitly synthetic and creates its own empty database. It never runs a real-person investigation. Existing synchronous operator commands remain available; the new worker runs versioned jobs with exact input bindings and separate publication checks.

## Try the new workflows

After running the acceleration demo:

```bash
statement-ledger --db data/demo-v02.sqlite3 search-claims "Synthetic Lab samples"
statement-ledger --db data/demo-v02.sqlite3 localize examples/localization-assist.json --out data/plan.json
statement-ledger --db data/demo-v02.sqlite3 estimate-cost examples/cost-input.json
statement-ledger --db data/demo-v02.sqlite3 calibration-report examples/calibration-labels.json
```

The bundled synthetic 10-minute case selects 315 seconds in assist mode, including audit
windows and padding, and retains both labeled target turns. This demonstrates code behavior,
not a claim about real speakers, actual diarization savings or model accuracy. Shadow mode
still processes all 600 seconds so exclusions can be audited.

Real profiles require accepted turns, confirmed speaker mappings, valid source dependencies,
comparison speakers and `learn_profile` permission. Candidate matching never creates an
accepted speaker mapping. Real media processing requires registered media hashes and rights;
the demo's URLs are deliberately not downloadable recordings.

## Enable Jev deliberately

Jev is **off by default**. The runtime also requires an explicit positive estimate and budget (`SL_REMOTE_ESTIMATE_MICRO_USD`, `SL_REMOTE_BUDGET_MICRO_USD`) before calls; unknown charges block automatic replay. See the foundation operating guide. The adapter uses the official TypeSafe endpoint, not a separate
Jev-branded service linked from a community article. Read
[the Jev contract chapter](docs/spec/26_JEV_TYPED_DECISION_BOUNDARY.md).

```bash
export SL_ENABLE_JEV=1
export TYPESAFE_API_KEY='your-own-key'
export SL_JEV_MODEL='jev-1.13.0'
statement-ledger --db data/your-authorized-workspace.sqlite3 localize localize-input.json --jev
```

PowerShell equivalents are `$env:SL_ENABLE_JEV="1"`, `$env:TYPESAFE_API_KEY="..."`, and
`$env:SL_JEV_MODEL="jev-1.13.0"`. Keys come only from server-side environment configuration.
All submitted source ancestry must permit `send_to_provider`. Provider request text and
raw responses are private retained records; backup and retention controls apply to them.

Noul scores and provider confidence are **not calibrated speaker-presence probabilities**.
Jev can suggest candidate regions or scoped-claim compatibility; it cannot approve identity,
merge propositions, authorize source access, or publish a factual conclusion. No paid/live
Jev invocation was performed for this release.

## Verification and development

```bash
python scripts/export-contracts.py
python scripts/compile-spec.py
python scripts/check-standalone.py
python -m pytest --cov=statement_ledger --cov-report=term-missing
```

Optional FFmpeg tests run when `ffmpeg`/`ffprobe` are installed. Real speech adapters require
separately provisioned libraries, permitted model weights and hardware. They are not hidden
base dependencies. The SpeechBrain comparison adapter requires explicit `process_biometrics`
permission and a locally provisioned model directory. Its score never confirms a name.

`python scripts/verify-ui.py` is an optional Playwright browser check. The release environment
blocked localhost browser navigation; API/static and JavaScript checks passed, but no visual
browser pass is claimed. See validation for the precise executed evidence.

## Synthetic index benchmark

`python scripts/benchmark-claims.py --records 10000` creates a temporary synthetic-only
workspace and reports ingest/search measurements. The included run stored 10,000 ambiguous
propositions in about 15.4 seconds and measured roughly 19.3 ms median search latency on this
execution environment. It includes no real claims, evidence-card joins, provider calls or
retrieval-quality assessment. See `validation/claim-index-benchmark.json`; do not extrapolate
these measurements into a million-record production guarantee.

## Production boundaries

This is a tested single-owner local research release, not a deployed mass-monitoring service.
Open work includes real provider/model acceptance, calibrated cross-program localization,
broad paraphrase retrieval, fitted acoustic thresholds, robust edited-video alignment,
public review/publication workflows, multi-user permissions, PostgreSQL scale, and measured
large real-corpus throughput. Source access and media redistribution rights remain explicit.

Do not derive a person's truthfulness, intentions or political merit from phrase features.
Keep speech-location signals and evidence judgments in different contracts. Every claim-level
finding remains linked to exact words, source context and reviewable evidence.

For a new remote repository, use the included Bash/PowerShell publishing helper from this
repository root after authenticating your own GitHub CLI. It defaults to a new private
repository and refuses an unrelated parent checkout. This delivery itself does not modify
any GitHub remote, original application, or source media account.
