# Phase 0 operating guide

The application remains standalone, single-owner, and research-only. No additional source was onboarded by this work. Runtime requirements are explicit migrations, a local filesystem, Docker Compose for the shared command surface, and no provider credentials for CPU tests. Direct Python commands remain available through a locked uv environment.

## Start and check

```bash
make up                 # Creates an ignored local token if missing; migrates; starts API and CPU worker.
make test               # Same container-backed test runner used by CI.
make check              # Lock consistency, Ruff, strict foundation types, boundaries, contracts, tests, proof.
make doctor             # Linked SQLite, Python/packages, FFmpeg, schema and model capability diagnostics.
make proof              # Synthetic queued import -> localization -> real FFmpeg -> correction -> restore.
make down               # Stops services; NEVER removes volumes.
```

PowerShell equivalents are `./scripts/dev.ps1 up`, `./scripts/dev.ps1 check`, etc. Python and Docker Compose must be installed on the host; no host virtual environment is mounted into a container. Source is mounted at `/workspace`; container packages live at `/opt/venv`. For native development: `uv sync --locked --group dev`, then `uv run --locked python scripts/check.py check`. Run `uv run --locked pre-commit install` to enable local hooks. CI repeats mandatory checks; local hooks are not the only gate.

The API is published only at `127.0.0.1:8765`. Its operator token is in ignored `.env`; no script prints it. Keep this file private. The existing browser expects that token, not a model-provider key. Changes to Python source are visible inside the dev container; restart long-lived workers after code changes. `compose.runtime.yaml` and the runtime Docker target avoid a source mount/dev dependencies; run an explicit migration with the same runtime image before starting it.

## Settings and credentials

Precedence is defaults < selected `[statement_ledger]` TOML < explicitly loaded dotenv < process environment < non-secret CLI overrides. Relative TOML paths use the TOML directory; environment/CLI paths use the working directory. `.env.example` is generated from settings metadata; `scripts/generate-environment.py --check` detects drift. Libraries do not silently load `.env`.

Use `SL_SECRET_API_TOKEN`, `SL_SECRET_TYPESAFE_API_KEY`, `SL_SECRET_YOUTUBE_API_KEY`, `SL_SECRET_FACTCHECK_API_KEY`, and `SL_SECRET_HF_TOKEN`. Transitional aliases are listed in `.env.example`; unequal aliases fail. `SL_SECRET_DIR` resolves files with the same logical names. TOML and command-line arguments are not secret stores. Disabled integrations need no credential. An enabled operation resolves and validates its required secret before work; credentials/permission failures do not produce empty successful results. Registry `credential_refs` describe only verified credential surfaces; an empty mapping does not mean every future vendor is anonymously accessible.

`statement-ledger config` is redacted by construction. Configuration errors identify fields without echoing values. Application worker logs contain allowlisted IDs/status/timing, not transcripts, provider bodies, exception text, URLs or tokens. Restricted provider-response bytes remain canonical SQLite receipts for compatibility and are included in private database backups; they are not logs. Vault adapters are deliberately not implemented.

## Data and upgrades

Default roots below `SL_DATA_ROOT`: `db`, `artifacts`, `raw`, `media`, `models`, `evaluation`, `scratch`, `backups`. Docker uses the existing `statement-ledger-data` named volume. Do not put the live SQLite file on SMB/NFS or in cloud-sync storage. Windows must use Linux-local Docker/WSL volume storage. Local CPU and optional GPU workers share this same-host database, not a network-mounted database.

The new default database is `data/db/ledger.sqlite3`. If `data/ledger.sqlite3` from the old runtime exists, migration refuses to create another empty ledger beside it: set `SL_DB_PATH` to the old file explicitly, take a native backup, then run `statement-ledger migrate`. API and workers NEVER perform startup DDL. Fresh tests/demos use an explicit bootstrap; `Store(initialize=True)` is retained only for disposable fixtures. New/runtime code uses `Store(path)` after migration.

Migrations 001-003 are contiguous SQL files with committed checksums. Do not edit applied migrations. Legacy v0.1/v0.2 records, hashes and audit rows are not rewritten. Unknown/future versions, changed checksums, partial schemas, and non-terminal legacy jobs fail closed. Finished legacy jobs are retained unchanged, including in-ledger jobs; they do not block migration. Custom legacy queue paths must be supplied via `--legacy-jobs` or `SL_LEGACY_JOBS_PATH`. Reconcile those jobs explicitly; they are never abandoned or guessed into new jobs.

DELETE journal mode is the safe default. WAL is allowed only for a documented fixed linked SQLite runtime (3.51.3+, 3.50.7 backport, or 3.44.6 backport). See the SQLite WAL documentation. Python dependency pinning does not pin the linked SQLite library. `doctor` records the actual runtime. Container bases and tools are digest/version pinned; OS package metadata and GPU hardware are also recorded/checked rather than claiming all platforms have identical binaries.

## Artifact registration and portable backup

`statement-ledger artifact-put FILE` streams an input into immutable SHA256-addressed storage and registers its checksum/size. Jobs refer to these keys, not arbitrary filesystem paths. Stage/check bytes before attaching references. Failed work may leave unregistered immutable objects; the local store can report them, but does not automatically delete evidence. Legacy synchronous import/analysis commands remain available; external files they reference must be registered separately before relying on a workspace backup to include their bytes.

```bash
make cli ARGS="artifact-put /workspace/path/to/authorized.vtt"
make backup ARGS="/data/backups/snapshot-001"
make restore ARGS="/data/backups/snapshot-001 /data/restored-001"
```

Stop/drain workers first; a backup with running jobs is refused. Backup takes a writer reservation and a SQLite snapshot, then verifies/copies registered immutable artifacts. The manifest explicitly excludes unregistered external files, model caches, scratch, and other backups. The snapshot includes canonical records, audit, outbox, jobs, attempts, provider operations and raw provider receipts. Restore verifies bytes, schema, reference inventory, record hashes and audit into a NEW directory. It never overwrites a running workspace. Restoring is the rollback mechanism; no destructive downgrade promise is made. Treat all backups as private evidence.

## Work and failure semantics

Use `statement-ledger config` for the execution fingerprint and version/hash bindings from the ledger. A `JobRequest` lists exact inputs, registered artifacts, handler/version, run ID, capability and configuration hash. Examples are generated in the synthetic proof; JSON schemas are in `contracts/runtime/`. Commands: `enqueue FILE`, `worker --once`, `worker`, `jobs`, `dispatch`, `cancel-job ID`, and `requeue-job ID --reason "reviewed recovery" --additional-attempts 1`. Authenticated equivalents include `/api/jobs` and cancellation. One GPU worker runs one job at a time.

Implemented handlers:
- `transcript.import` (CPU): retained VTT/SRT/ASR artifact -> proposed transcript.
- `speech.localize` (CPU): current profile/transcript -> shadow-mode localization plan by default.
- `media.clip` (CPU): matching registered media -> FFmpeg audio clip and provenance manifest.
- `jev.decision` (CPU/network, opt-in): explicit source-bound typed request -> advisory decision record and cost/response receipts.
- `speech.transcribe` (GPU, opt-in): pre-provisioned immutable model + approved media -> ASR transcript with UNASSIGNED speakers.

The core transaction accepts records, immediately invalidates descendants, and writes audit/outbox together. The dispatcher atomically inserts/deduplicates jobs and acknowledges work intents. Unsubscribed record events are retained as `unhandled`, not interpreted as permission to run another source/model. Phase 0 deliberately does not install an autonomous scheduler.

Workers claim, renew leases using an independent connection, prepare outside database transactions, then atomically recheck input revisions, current rights, configuration and lease ownership before attaching outputs and completing. Cancellation/lease loss prevents publication. Handler retries are bounded; there is no exactly-once external-call guarantee. Repeated local jobs do not produce repeated canonical effects. Strict input changes require a new reviewed request. Follow run/job/attempt IDs through structured logs, queue rows and audit records.

For Jev, set `SL_ENABLE_JEV=1`, the credential, a positive `SL_REMOTE_ESTIMATE_MICRO_USD`, and `SL_REMOTE_BUDGET_MICRO_USD`. Estimates reserve a local budget, NOT a guarantee that a provider cannot bill more. Actual usage is retained; unavailable pricing/ambiguous charges stay `unknown`, never zero. The operation is persisted before the call. An ambiguous attempt blocks automatic replay. `operations` inspects records; `reconcile-operation ID --actual-micro-usd N --evidence TEXT` requires explicit operator evidence. No paid calls run in CI or the proof.

## GPU prerequisites and real experiment

`make gpu` builds the separate Python 3.11 CUDA-compatible environment and requests one NVIDIA GPU. It does not acquire model weights or accept model licenses. Provision authorized CTranslate2 files under ignored `local-models/whisper`, then use `python scripts/model-manifest.py local-models/whisper --revision PINNED_REVISION --confirm-rights`. Keep the directory immutable and mounted read-only. Use a new versioned name for a different model. The manifest hash is required in a GPU job. `docker compose --profile gpu run --rm --no-deps gpu-worker statement-ledger doctor --gpu` must confirm real device availability. CPU CI and dependency resolution are not GPU-inference proof.

Keep the real-recording experiment bounded and held out. It still requires authorized recordings, reviewed speaker labels, actual GPU/model provision, and explicit provider-spend choices. Compare whole-file, phrase-only and Jev-assisted routing on the same corpus; retain coverage, wrong attribution, selected duration, full cost and human effort. No profile promotion or savings claim follows from the synthetic proof.

## Recovery after review fixes

Repeated enqueue returns the existing job state and `requeue_required`; it does not silently
revive terminal work. Explicit authenticated requeue grants bounded additional attempts and
retains all old attempt ordinals/receipts. It never skips current inputs, rights or cancellation
checks. Ambiguous paid operations stay blocked even after requeue or cost reconciliation.
Successful source-bound Jev proposals are persisted before canonical publication and can be
recovered after database contention without paying twice. Cancellation is checked before
reservation and before transport; only a known-unsent call releases its budget as zero cost.
See [review remediation](../PR1_REVIEW_FIXES.md) for the twelve regressions and limitations.

`SL_RUN_LIVE` is a recognized test-runner control, not a provider-spending switch. The main
branch's exact-marker live gate is retained: tests needing providers, secrets or actual GPU
execution are skipped in ordinary checks. Never set it in cloud-agent CI to avoid the gate.
