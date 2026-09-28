---
id: SL-002
title: "Resolve a reproducible dependency and model environment"
status: proposed
gate: G1
dependencies: ["SL-001"]
---

# SL-002: Resolve a reproducible dependency and model environment

## Objective and boundaries

Create reviewed, platform-specific dependency lock/constraints after registry access returns. Pin optional ASR and diarization packages, model revisions, CUDA/runtime requirements and licenses separately from the CPU API environment.

This work belongs only to this standalone repository. Do not copy application-specific contracts, source credentials or a canonical database from another product. The current delivery state is `proposed`; future acceptance criteria are not completed merely because they are written here.

## Acceptance criteria

- [ ] Clean install on declared Python 3.11, 3.12 and 3.13 targets or narrow support honestly.
- [ ] Generate a reviewed dependency/SBOM and vulnerability report with an explicit check date.
- [ ] Demonstrate optional speech dependencies do not become mandatory for ordinary API startup.

## Required adversarial case

A lock contains invented hashes or claims that an untested GPU environment was validated.

## Implementation surfaces

- `pyproject.toml`
- `.github/workflows/ci.yml`
- `docs/DEPENDENCIES.md`

## Validation and completion evidence

Retain the exact command, environment, fixture or permitted source hash, result, and unresolved limitations. Mocked transport proves client behavior only; a source integration requires an authorized real fixture and bounded live proof. A model/throughput claim requires a real run. Add regression tests for both acceptance and refusal paths; regenerate affected schemas and specification before closing the ticket.

## Rollback

Keep the feature disabled until its gate passes. On regression, stop the new producer/consumer, preserve immutable record history and audit evidence, and restore the previously validated behavior. Do not erase conflicting evidence or reapprove stale descendants merely to recover green status.
