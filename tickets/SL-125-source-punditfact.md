---
id: SL-125
title: "Onboard PunditFact"
status: access_and_contract_gate
gate: G2
dependencies: ["SL-003", "SL-004", "SL-006"]
source_id: punditfact
---

# SL-125: Onboard PunditFact

## Input contract

Role: `review_discovery`. Access requirement: `publisher_terms`. Current delivered surface: `contract_only`. This ticket does not describe a live connection.

Read [the source-specific worksheet](../docs/sources/punditfact.md) for native input semantics, the first acquisition experiment and a source-specific hard negative. The relevant boundary is: A PolitiFact collection; do not double-count a review discovered through both.

## First action

Link to canonical publisher review; trace its source broadcast.

## Acceptance criteria

- [ ] Confirm the actual authorization, intended operations, source version and current documentation; keep account credentials outside the repository.
- [ ] Acquire a bounded permitted real sample and retain a hash plus redacted test fixture, or explicitly record that access is blocked.
- [ ] Map native IDs, uncertain dates, text roles and source references to observations without promoting them to verified utterances or first-party findings.
- [ ] Exercise the worksheet's adversarial case, malformed payloads, pagination/resume, duplicate replay and changed source versions.
- [ ] Produce a source/date coverage receipt and an honest list of missing records/media, unverified fields and contractual limits.
- [ ] Only after real proof, change that source's live verification metadata; leave other sources untouched.

## Integration boundaries

A format-level source such as ClaimReview is not an additional independent publisher. A vendor platform subscription is not automatically a data redistribution license. A quote count is not an independent spoken-occurrence count. Never invent an API route for a contract-only source. Use the authorized manual envelope when that is the supported path and label it accordingly.

## Evidence and rollback

Attach exact sample hashes, parser version, commands/results, dated entitlement and review notes. Tests must demonstrate that a schema failure cannot become an empty successful result. On failure, disable this source's active intake, retain permitted provenance, and expose a coverage gap. No other source or project should be modified to disguise the missing integration.
