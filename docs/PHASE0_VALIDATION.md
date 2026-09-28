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

Unavailable in the local editing sandbox: external DNS, Docker, a GPU, real model
weights, live provider credentials, authorized real-person audio, and browser navigation.
No live calls, real-person statements, fabricated findings or claimed production speedups
were used to substitute for those missing prerequisites. Hardware/runtime-specific
acceptance remains explicit in the operating guide.
