# Phase 0 implementation status

Implementation target: the agreed foundation plan, not an expanded source/product scope.

| Package | Delivered | Evidence / boundary |
|---|---|---|
| P0-01 | Current GitHub baseline preserved; stale remote-repo status corrected | Main ffcb18b and all 47 source entries retained. Visibility, copyright notice, personal identity and existing history unchanged. |
| P0-02 | CPU dev/runtime images, committed CPU/GPU locks, pinned base digests, Make/PowerShell front door | Lock resolution ran on GitHub; actual CPU container checks are CI gates. Real 4070 execution is separate. |
| P0-03 | Typed settings, env/file secrets, aliases, generated example, safe logs, Ruff, foundation strict types, Gitleaks hooks/CI | Legacy moved modules remain outside strict mypy; they are formatted/linted and retain tests. See explicit checked file list; no global ignore-errors switch. |
| P0-04 | Numbered/checksummed SQL, legacy adoption, local artifact store, verified workspace backup/restore | External unregistered files/model cache are explicitly excluded; provider BLOB receipts remain in the canonical DB. No cloud store implementation. |
| P0-05 | Core/contracts/infrastructure/application and six real domain owners; read-only validator views and sealed registration | Static boundary check plus deliberate forbidden-import test. Root compatibility facades preserve existing imports. |
| P0-06 | Same-DB queue/outbox, worker loop/heartbeats/cancellation/retries/fencing, operation receipts, real handlers | Local handlers exercised on synthetic inputs; network adapter tests do not authorize live spending. Record events remain unsubscribed until an explicit workflow is approved. |
| P0-07 | Integrated queued transcript/localization/FFmpeg proof, duplicate replay, restart, immediate correction, backup/restore | Synthetic proof only. Real corpus, live Jev, actual GPU inference and human speaker evaluation remain blocked on external prerequisites. |

Run `make check` and `make proof`; the runbook describes installation, migration and recovery.
The original 29 product chapters are retained as design history and targets. This file and
`docs/IMPLEMENTATION_STATUS.md` distinguish current implementation from future features.
No PostgreSQL, Redis, public publication, multi-user SaaS, automatic source crawling,
remote SQLite mounting or mandatory private-project integration was introduced.
