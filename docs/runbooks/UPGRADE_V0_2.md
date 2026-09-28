# Upgrade to v0.2.0

This is a replacement package for the same standalone repository, not a new product
coupled to any other application. No GitHub remote is created or modified by the package.

## Protect existing work

Stop the application. Keep the original code/archive and take a native SQLite backup.
With the old environment active:

```bash
statement-ledger --db data/ledger.sqlite3 verify
statement-ledger --db data/ledger.sqlite3 backup backups/before-v0.2.sqlite3
```

Choose a destination that does not exist. Do not replace a nonempty working tree without
committing or backing up local changes. Unpack the new repository into a separate folder,
install it in a new virtual environment, and point it at a COPY of the database first.
Do not copy a package's synthetic database into your real workspace; no database is shipped.

## Install and verify

```bash
python -m venv .venv
# Bash: source .venv/bin/activate
# PowerShell: .\.venv\Scripts\Activate.ps1
python -m pip install -e ".[test]"
python -m pytest -q
python scripts/check-standalone.py
statement-ledger --db data/upgrade-test.sqlite3 verify
statement-ledger --db data/upgrade-test.sqlite3 reindex-claims
```

For a real upgrade, `data/upgrade-test.sqlite3` must be your copied old database; an empty
path initializes an empty workspace and is not evidence of a successful migration of
existing data. The additive migration preserves original revisions and builds the search
projection. Review old data with unknown new scope fields before permitting evidence reuse.

## Run the new demonstration separately

```bash
statement-ledger --db data/acceleration-demo.sqlite3 demo-acceleration
statement-ledger --db data/acceleration-demo.sqlite3 search-claims "Synthetic Lab samples"
```

The acceleration demo requires an empty database. It creates only fictional data and makes
no model calls. It prints profile IDs, both plans, a labeled-window evaluation and claim
search results. Use the printed plan ID when running subsequent evaluation commands.

## Start the private interface

Generate an application token and set it in the shell; `.env.example` is documentation,
not an automatic dotenv loader. PowerShell:

```powershell
$env:SL_API_TOKEN = python -c "import secrets; print(secrets.token_urlsafe(40))"
statement-ledger --db data/acceleration-demo.sqlite3 serve
```

Bash:

```bash
export SL_API_TOKEN="$(python -c 'import secrets; print(secrets.token_urlsafe(40))')"
statement-ledger --db data/acceleration-demo.sqlite3 serve
```

Open the local server at port 8765 and enter the token. Inspect Phrase profiles, Speaker
windows and Claim library. The browser's Build local plan button does not call Jev.
No visual smoke-test success is claimed where browser policy blocked execution.

## Enable the official optional provider deliberately

```powershell
$env:SL_ENABLE_JEV = "1"
$env:TYPESAFE_API_KEY = "YOUR_OWN_KEY"
$env:SL_JEV_MODEL = "jev-1.13.0"
statement-ledger --db data/acceleration-demo.sqlite3 localize examples/localization-assist.json --jev
```

Use corresponding `export` statements in Bash. Do not put real keys in a committed file,
command transcript, public issue or browser bundle. All source dependencies must allow
`send_to_provider`. A missing permission rejects the call. No calibration or throughput
claim follows merely from receiving a valid response.

## Roll back

Stop v0.2, copy its database aside, restore the pre-upgrade native backup, and reactivate
the old environment/code. Do not delete the new database before preserving research added
after upgrade. New profiles, cards and receipts will not exist in the restored backup.
