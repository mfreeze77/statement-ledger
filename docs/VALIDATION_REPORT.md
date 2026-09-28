# Statement Ledger v0.2.0 — validation and release evidence

Release date: September 27, 2026. Specification: 1.1. All real people remain unpopulated
research subjects; the executed demonstrations and load corpus are fictional.

## Result summary

| Check | Executed result | Scope |
|---|---|---|
| Uploaded v0.1.0 baseline, independently extracted | 126 passed | Original tests rerun without code changes |
| Expanded v0.2.0 suite | 227 passed | Includes 101 additional tests; original tests retained except updated schema-kind expectation |
| Python statement coverage | 90.68% (2208/2435) | Line/statement coverage, not branch or real-data accuracy |
| Canonical schemas and API snapshot | Passed | 20 record kinds; additional seed/config contracts generated from implementation |
| Standalone namespace/configuration guard | Passed | No other private application's runtime coupling introduced |
| Ticket dependencies and documentation links | Passed in suite | 85 ticket records, 34 source worksheets, no broken local Markdown links |
| Python compile check and JavaScript syntax | Passed | No browser visual claim implied |
| Local FFmpeg/ffprobe | Passed on synthetic WAV | Selected clipping and duration checked; real codec/media matrix not established |
| Jev transport/orchestration | Passed mocked transport tests | No live or paid provider invocation |
| Speech inference adapters | Passed fake model tests | No actual ASR, diarization or ECAPA weights/inference executed |
| Installed wheel smoke | Passed | Version 0.2.0, synthetic demo, static assets; preinstalled dependencies |
| Browser smoke | Blocked | Chromium launched; localhost navigation returned ERR_BLOCKED_BY_ADMINISTRATOR |

The complete specification contains 29 chapters and approximately 21,865 whitespace-
separated words. Six upgrade chapters extend—not replace—the original independent design.
Source onboarding is still explicit; naming a service does not mean it is connected.

## Executed commands

```bash
# In a separate extraction of the uploaded original:
python -m pytest -q

# In the upgraded repository:
python scripts/export-contracts.py
python scripts/compile-spec.py
python scripts/check-standalone.py
python -m compileall -q src scripts
node --check src/statement_ledger/static/app.js
python -m pytest --cov=statement_ledger --cov-report=term-missing --cov-report=json:validation/coverage.json
python -m pytest -q
python scripts/benchmark-claims.py --records 10000
python -m pip wheel . --no-build-isolation --no-deps --wheel-dir /mnt/data/v02-dist
python -m pip install --no-deps --target /mnt/data/v02-wheel-installed /mnt/data/v02-dist/statement_ledger-0.2.0-py3-none-any.whl
```

The installed-wheel smoke imported from the installation target outside the source checkout,
ran `demo-acceleration` in a temporary empty database and checked packaged HTML, JavaScript
and CSS. It used already installed dependencies. It is **not** a clean network-resolved
installation proof. The version in both package metadata and module is 0.2.0.

## Synthetic end-to-end localization

The demonstration has three target training events and three comparison-speaker events.
Its independent held-out synthetic asset is 600 seconds long with two labeled 10-second
target turns. In assist mode the planner selects 315 seconds after overlapping-window
merging, context padding and rejected-window audits. Both target turns fall inside the
selection. Shadow mode selects all 600 seconds. The original example still groups three
assets into two exact aligned original occurrences and one proposition.

The 47.5% reduction is **selected audio duration in a constructed fixture**, not measured
real-world diarization savings. No actual named person's speech was tested. Jev is not
called in this fixture. The label completeness flag belongs to this constructed case.
The result cannot validate a probability threshold or approve an identity automatically.

## Synthetic claim-index measurement

A separate temporary SQLite database received 10,000 ambiguous synthetic
propositions through the actual ledger write path. No reviews or factual findings were
created. Measured on 3.13.5 / Linux-6.18.44-x86_64-with-glibc2.41:

| Measurement | Result |
|---|---:|
| Ingest duration | 15.375 seconds |
| Ingest rate | 650.42 records/second |
| Search requests | 50 |
| Median query latency | 19.269 ms |
| Empirical p95 query latency | 20.323 ms |
| Database size after checkpoint | 22,323,200 bytes |

These are local measurements for this synthetic distribution. They do not include live
source downloads, article parsing, evidence-card ancestry expansion, semantic retrieval,
concurrent users, embedding generation, full video work or review time. All 50 queries
returned their requested 20 results; that is not a relevance-quality benchmark. A larger
real-corpus and production-storage gate remains open.

## Correctness and refusal paths exercised

Profiles reject unaccepted/stale/unauthorized examples and target-as-background contamination.
Event support deduplicates repeated uploads. Refresh retains explicit comparisons and holdout
exclusions. Unknown caption gaps, cold starts, no candidates, incomplete semantic batches and
provider faults do not silently discard audio. Interval unions preserve half-open timebases.
Adjacent gold turns remain two turns even when their time coverage is contiguous.

Jev tests validate the official endpoint, server-side secret handling, byte budgets, retries,
timeouts, raw capture before parsing, malformed JSON and duplicate keys, finite numeric types,
model/legend/question consistency, independently quantized results, capture hashes, source
rights, request/revision-sensitive cache keys and advisory claim comparisons. A false semantic
compatibility suggestion cannot override structured scope mismatches or create a review.

Claim tests exercise exact seed dedup, rejected imported verdict fields, expiry, open corrections,
missing scope, primary-evidence relevance and legacy record compatibility. Old payloads and
hashes are not rewritten on additive migration. Non-UTF-8 provider bytes survive JSON export
through base64. Native backups use SQLite's backup API.

Media execution tests check input hashes, confined paths, output-exists refusal, FFmpeg output,
source offsets, clip-local speaker labels, manifested failures and advisory acoustic output.
Provider and inference fakes remain distinguishable from actual media execution.

## Unexecuted or blocked gates

No TypeSafe API key was used and no billed request was sent. No real external source corpus
was harvested. No ASR/diarization/acoustic model weights were downloaded or run. The wrapper
contracts must pass authorized live acceptance before real deployment. No measured Jev latency,
model accuracy, human-speaker attribution reliability or calibrated probability is reported.

Playwright's browser launched using system Chromium, but navigation to the local test server
was blocked by environment administration. No attempt was made to evade that restriction.
Static route tests and JavaScript syntax checks passed; interactive visual validation remains
open. Reproduction script: `scripts/verify-ui.py`. Result: `validation/ui-smoke.json`.

Docker runtime execution, PowerShell execution, Python 3.11/3.12 runtime tests and the GitHub CI
matrix were not executed here. The CI configuration remains provided for those environments.
Full dependency resolution from an empty environment, remote repository creation and deployment
were not performed. No public sharing, multi-user access or production rollout is claimed.

The application remains single-owner SQLite research software. Calibration fitting/promotion,
large-scale semantic retrieval, robust edited-event matching, automatic accepted-turn workers,
real source onboarding, complete retention/purge and collaborative review remain bounded tickets.

## Evidence files

- `validation/baseline-pytest.txt`
- `validation/pytest-output.txt` and `validation/pytest-final.txt`
- `validation/coverage.json`
- `validation/claim-index-benchmark.json`
- `validation/wheel-build.txt`, `validation/wheel-install.txt`, `validation/wheel-smoke.json`
- `validation/ui-smoke.json`

Artifact extraction/bundle verification is recorded separately during final packaging. This
report does not assert a successful verification before that command has actually completed.
