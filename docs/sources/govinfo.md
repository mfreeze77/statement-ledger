# GovInfo API — source intake worksheet

Registry ID: `govinfo`. Role: `primary_evidence`. Access: `api_key`.
Delivery state: **contract_only**. Live verification: **not performed**. This page is an integration contract and investigation plan, not proof of current account entitlement.

## Inputs and semantic mapping

Collection, package and granule identifiers, publication date, document text or PDF, and page locators. Hearing transcripts are primary evidence of what was said, not of whether it was true.

Keep source-native IDs, original payload, parser version, retrieval time, and source grant. A retrieved record is evidence bearing on a proposition, never a finding by itself; scope (date, geography, quantity, definition and version) must match the proposition before a reviewer relies on it. Emit an `Observation` first; a reviewer or subsequently validated workflow establishes which proposition, if any, the record bears on.

## Initial acquisition experiment

Retrieve a Congressional Record granule and confirm a cited passage resolves to the exact page and retained revision.

Current next step: Request an API key; capture a bounded document package and retain its package identifier and granule locator.

Use a bounded sample, declared date range, page/byte limits, query fingerprint, and restart cursor. Save a receipt that distinguishes a genuinely empty permitted result from blocked access, parse failure, missing asset, expired link and exhausted page budget. Never expand scope or purchase access automatically.

## Rights and retention checklist

Record whether the granted operations cover metadata discovery, text retention, local audio processing, derivative clips, external-model transfer and publication. These permissions are independent. Record expiry and a source document or contract reference. A source's homepage or search availability is not a media reuse grant. Vendor samples must remain private unless their redistribution is explicitly authorized.

## Hard-negative test

A retrieval summary cites a page number that does not exist in the retained package.

Also test missing required fields, repeated imports, source revisions, deleted links, uncertain dates and unexpected response shape. Parsing success does not establish factual accuracy or identity. An unsupported native response must fail explicitly rather than produce zero observations.

## Acceptance evidence

The connector graduate must supply the permitted sample hash, contract/documentation date, redacted fixture, parser mapping, test command/result, declared coverage and unresolved limitations. A registered source remains visible as blocked when access is unavailable. Claim no live support until a real bounded run has passed.

## Existing boundary

Official published documents (Congressional Record, statutes, hearings, budget documents); publication dates can lag events.

## Source references

- https://www.govinfo.gov/developers

These are provider/documentation pointers. The status matrix and validation report, not the presence of a link, determine which integrations were exercised. Re-check dated articles and commercial terms before production use.
