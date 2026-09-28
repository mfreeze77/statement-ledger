# CourtListener API — source intake worksheet

Registry ID: `courtlistener`. Role: `primary_evidence`. Access: `api_token`.
Delivery state: **contract_only**. Live verification: **not performed**. This page is an integration contract and investigation plan, not proof of current account entitlement.

## Inputs and semantic mapping

Court, docket number, case name, document type, filing or decision date, text and citation. Allegations in a complaint are not findings of fact.

Keep source-native IDs, original payload, parser version, retrieval time, and source grant. A retrieved record is evidence bearing on a proposition, never a finding by itself; scope (date, geography, quantity, definition and version) must match the proposition before a reviewer relies on it. Emit an `Observation` first; a reviewer or subsequently validated workflow establishes which proposition, if any, the record bears on.

## Initial acquisition experiment

Retrieve a docket with a complaint and a later ruling and confirm each is scoped to its own document type.

Current next step: Request an API token; capture a bounded docket and opinion sample and record court, docket number and document type.

Use a bounded sample, declared date range, page/byte limits, query fingerprint, and restart cursor. Save a receipt that distinguishes a genuinely empty permitted result from blocked access, parse failure, missing asset, expired link and exhausted page budget. Never expand scope or purchase access automatically.

## Rights and retention checklist

Record whether the granted operations cover metadata discovery, text retention, local audio processing, derivative clips, external-model transfer and publication. These permissions are independent. Record expiry and a source document or contract reference. A source's homepage or search availability is not a media reuse grant. Vendor samples must remain private unless their redistribution is explicitly authorized.

## Hard-negative test

A claim that someone 'was found' to have done something is supported only by allegations in a complaint.

Also test missing required fields, repeated imports, source revisions, deleted links, uncertain dates and unexpected response shape. Parsing success does not establish factual accuracy or identity. An unsupported native response must fail explicitly rather than produce zero observations.

## Acceptance evidence

The connector graduate must supply the permitted sample hash, contract/documentation date, redacted fixture, parser mapping, test command/result, declared coverage and unresolved limitations. A registered source remains visible as blocked when access is unavailable. Claim no live support until a real bounded run has passed.

## Existing boundary

Court opinions, dockets and oral-argument audio; docket coverage is incomplete and a filing is not a ruling.

## Source references

- https://www.courtlistener.com/help/api/

These are provider/documentation pointers. The status matrix and validation report, not the presence of a link, determine which integrations were exercised. Re-check dated articles and commercial terms before production use.
