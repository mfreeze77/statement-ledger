# Local operations and reproducibility

## Installation and launch

Use README instructions in a new virtual environment. The initial verification used an already provisioned Python environment; a clean install still requires package-registry access. Direct runtime versions are pinned, but no cross-platform hash lock was produced because dependency resolution was unavailable. `proof/tested-environment.json` is an observed environment, not a universal installer.

The server must remain bound to loopback by default. Set a fresh random `SL_API_TOKEN` with at least 32 characters. Never put real secrets in `.env.example`, source fixtures or issue bodies. The Docker Compose file is a local deployment scaffold, not evidence of a tested production container rollout.

## Test and regenerate contracts

```bash
python -m pytest -q
python scripts/check-standalone.py
python scripts/export-contracts.py
python scripts/compile-spec.py
node --check src/statement_ledger/static/app.js
```

Review generated diffs. Tests use synthetic fixtures and mocked external responses unless the validation report explicitly says otherwise. Do not change frozen expected values merely to make a new implementation pass without understanding the semantic change.

## Backup and restore

```bash
statement-ledger --db data/research.sqlite3 verify
statement-ledger --db data/research.sqlite3 backup backups/research-2026-09-27.sqlite3
statement-ledger --db backups/research-2026-09-27.sqlite3 verify
```

Choose a new destination; the command refuses an existing file. It uses SQLite's online backup API rather than copying an active WAL database arbitrarily. Back up retained raw files and a grant/retention inventory separately. A database backup does not contain external raw/media files. Restore into a disposable local workspace, compare counts and integrity checks, and reproduce selected dependency chains before replacing an operational instance.

## Git publication

The supplied project is independent. The archive contains the source tree; the Git bundle preserves the initial commit. Clone the bundle into a new directory and remove its local bundle origin before running the publishing helper, or initialize/commit the source ZIP with your own Git author. Never run the helper from a parent repository. The helper must verify its working tree root exactly matches this project, refuse existing origin, refuse dirty files and use private visibility.

```bash
git clone statement-ledger.bundle statement-ledger
git -C statement-ledger remote remove origin
cd statement-ledger
bash scripts/publish-github.sh mfreeze77/statement-ledger
```

GitHub CLI must already be installed and authenticated. This delivery did not create a remote repository. Public visibility is a separate deliberate action; research data and credentials must never be committed.
