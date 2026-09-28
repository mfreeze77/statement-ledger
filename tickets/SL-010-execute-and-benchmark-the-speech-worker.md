---
id: SL-010
title: "Execute and benchmark the speech worker"
status: proposed
gate: G3
dependencies: ["SL-002", "SL-005"]
---

# SL-010: Execute and benchmark the speech worker

## Objective and boundaries

Run the optional transcription/diarization adapters on permitted recordings with exact model revisions and resource settings. Record processing provenance and evaluate turn/word quality.

This work belongs only to this standalone repository. Do not copy application-specific contracts, source credentials or a canonical database from another product. The current delivery state is `proposed`; future acceptance criteria are not completed merely because they are written here.

## Acceptance criteria

- [ ] Capture actual model outputs, hardware, run duration, memory use and input hashes.
- [ ] Benchmark overlap, names, numbers, negations, music, silence and multilingual passages.
- [ ] Low-quality segments enter review; no named identity is assigned by diarization alone.

## Required adversarial case

An ASR hallucination during silence becomes an accepted factual assertion.

## Implementation surfaces

- `src/statement_ledger/speech.py`
- `tests/speech/`
- `docs/evaluation/`

## Validation and completion evidence

Retain the exact command, environment, fixture or permitted source hash, result, and unresolved limitations. Mocked transport proves client behavior only; a source integration requires an authorized real fixture and bounded live proof. A model/throughput claim requires a real run. Add regression tests for both acceptance and refusal paths; regenerate affected schemas and specification before closing the ticket.

## Rollback

Keep the feature disabled until its gate passes. On regression, stop the new producer/consumer, preserve immutable record history and audit evidence, and restore the previously validated behavior. Do not erase conflicting evidence or reapprove stale descendants merely to recover green status.
