# Phase 0 validation evidence

Baseline: `ffcb18bca3b229772418c6fdb64087a3f161a54f` (GitHub source additions preserved).
Local validation uses Python 3.13.5, linked SQLite 3.46.1 in DELETE mode and real FFmpeg.

Executed locally during implementation:
- Existing regressions plus new foundation tests: all passed (the final PR CI log is authoritative for counts).
- Ruff 0.14.10 formatting/lint checks over the repository.
- mypy 1.19.1 strict checks for the 14 explicitly listed foundation modules.
- CPU uv lock consistency, generated schemas and module-boundary checks.
- Integrated synthetic worker proof: transcript import, duplicate replay, localization,
  real FFmpeg clipping, restart, immediate downstream invalidation and verified restore.
- Legacy populated migration preserving exported records/audit, migration rollback/retry,
  competing migrators, bad/future checksums, malformed dispatch rollback, cancellation,
  heartbeat across lease duration, revoked rights and stale output rejection.

GitHub tooling resolution ran in `phase0-toolchain`, run 36369732696: both CPU and
optional GPU locks resolved successfully and container image digests were retrieved.
That resolution is NOT evidence of GPU installation or inference. The temporary tooling
workflow is removed from the final tree. Standard CI runs the actual locked test suite,
container bootstrap/readiness/auth checks, and redacted secret scanning.

## Resumption: security and CI gates

The interrupted run left PR #1 with a failing secret scan. Three detections were
independently reproduced synthetic event hashes, not credentials. The remediation
and positive/negative controls are documented in `SECRET_SCAN_REVIEW.md`; the full
history scanner and all five actual scanner controls passed on GitHub at `31cc611`.

Inspecting that run's archived check output revealed another problem: the implicit
Actions shell allowed `tee` to hide a formatting failure. Its green job status did
NOT prove later type/test/proof gates ran. Do not use that intermediate green status
as final verification. CI now selects Bash with pipefail and retains stderr as well
as stdout. Regression tests exercise propagation of failures. The check runner emits
`FOUNDATION_CHECK_COMPLETE` only after every gate, including the integrated proof,
completes; CI also requires the completion marker in the captured output.

A second CI defect was found in the actual interpreter logs: `.python-version` made
uv select Python 3.13 even in jobs labelled 3.11 and 3.12. CI now sets `UV_PYTHON`
from the matrix, disables interpreter downloads, and asserts the running major/minor
version. Historical job names alone are not evidence of multi-version coverage.

The resumption fetched the exact source archive from GitHub Actions. **298 tests
passed locally** after correction. Ruff 0.14.10 and mypy 1.19.1 were downloaded as
pinned wheels by a temporary read-only GitHub job (36376561821), then installed
locally without network access. Ruff formatting/lint and strict checks on all 14
foundation files passed. The queued import/localization/FFmpeg proof, immediate
invalidation, backup/restore, boundaries and generated-environment checks also passed.
Temporary editor/toolchain workflows are removed from the delivered tree.

The final PR CI run is authoritative for locked dependencies, the explicitly checked
Python versions and the actual container workflow. Verify the completion markers and
pytest counts in its artifacts, not only a green badge. The source archive contains
tracked files and its tested Git merge SHA. No generated data or credentials belong
in that archive.

Unavailable in the local editing sandbox: external DNS, Docker, a GPU, real model
weights, live provider credentials, authorized real-person audio, and browser navigation.
No live calls, real-person statements, fabricated findings or claimed production speedups
were used to substitute for those missing prerequisites. Hardware/runtime-specific
acceptance remains explicit in the operating guide.
