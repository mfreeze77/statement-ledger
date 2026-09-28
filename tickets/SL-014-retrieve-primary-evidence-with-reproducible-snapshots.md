---
id: SL-014
title: "Retrieve primary evidence with reproducible snapshots"
status: proposed
gate: G5
dependencies: ["SL-005", "SL-013"]
---

# SL-014: Retrieve primary evidence with reproducible snapshots

## Objective and boundaries

Add a generic retrieval port and permitted evidence capture without depending on any other product. Preserve full query provenance, source snapshots, exact locators and evidence cut-off times.

The registry's `primary_evidence` entries (SL-139 to SL-147: Congress.gov, GovInfo, Federal Register, BLS, Census, FRED, OpenFEC, CourtListener and other official publications) are the first retrieval targets. Each is contract-only until its own onboarding ticket passes.

This work belongs only to this standalone repository. Do not copy application-specific contracts, source credentials or a canonical database from another product. The current delivery state is `proposed`; future acceptance criteria are not completed merely because they are written here.

## Acceptance criteria

- [ ] A cited passage resolves in the exact retained source revision.
- [ ] External reviews stay attributed secondary research rather than being silently retyped primary.
- [ ] Duplicate secondary articles that share one source are not independent evidence.

## Required adversarial case

A retrieval summary invents a page number or quotes content absent from the source.

## Implementation surfaces

- `src/statement_ledger/retrieval.py`
- `src/statement_ledger/models.py`
- `tests/test_evidence_capture.py`

## Validation and completion evidence

Retain the exact command, environment, fixture or permitted source hash, result, and unresolved limitations. Mocked transport proves client behavior only; a source integration requires an authorized real fixture and bounded live proof. A model/throughput claim requires a real run. Add regression tests for both acceptance and refusal paths; regenerate affected schemas and specification before closing the ticket.

## Rollback

Keep the feature disabled until its gate passes. On regression, stop the new producer/consumer, preserve immutable record history and audit evidence, and restore the previously validated behavior. Do not erase conflicting evidence or reapprove stale descendants merely to recover green status.
