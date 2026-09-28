# Federal Register API — source intake worksheet

Registry ID: `federal_register`. Role: `primary_evidence`. Access: `public_api`.
Delivery state: **contract_only**. Live verification: **not performed**. This page is an integration contract and investigation plan, not proof of current account entitlement.

## Inputs and semantic mapping

Document number, type, agency, publication and effective dates, docket identifiers and full text. Document type and effective date are part of the evidence scope.

Keep source-native IDs, original payload, parser version, retrieval time, and source grant. A retrieved record is evidence bearing on a proposition, never a finding by itself; scope (date, geography, quantity, definition and version) must match the proposition before a reviewer relies on it. Emit an `Observation` first; a reviewer or subsequently validated workflow establishes which proposition, if any, the record bears on.

## Initial acquisition experiment

Retrieve a proposed rule and its final rule and confirm each is scoped to its own type and date.

Current next step: Capture a bounded document sample and record document type, docket and effective date.

Use a bounded sample, declared date range, page/byte limits, query fingerprint, and restart cursor. Save a receipt that distinguishes a genuinely empty permitted result from blocked access, parse failure, missing asset, expired link and exhausted page budget. Never expand scope or purchase access automatically.

## Rights and retention checklist

Record whether the granted operations cover metadata discovery, text retention, local audio processing, derivative clips, external-model transfer and publication. These permissions are independent. Record expiry and a source document or contract reference. A source's homepage or search availability is not a media reuse grant. Vendor samples must remain private unless their redistribution is explicitly authorized.

## Hard-negative test

A claim about current policy is checked against a proposed rule that was never finalized.

Also test missing required fields, repeated imports, source revisions, deleted links, uncertain dates and unexpected response shape. Parsing success does not establish factual accuracy or identity. An unsupported native response must fail explicitly rather than produce zero observations.

## Acceptance evidence

The connector graduate must supply the permitted sample hash, contract/documentation date, redacted fixture, parser mapping, test command/result, declared coverage and unresolved limitations. A registered source remains visible as blocked when access is unavailable. Claim no live support until a real bounded run has passed.

## Existing boundary

Rules, proposed rules, notices and presidential documents; a proposed rule is not a final rule.

## Source references

- https://www.federalregister.gov/developers/documentation/api/v1

These are provider/documentation pointers. The status matrix and validation report, not the presence of a link, determine which integrations were exercised. Re-check dated articles and commercial terms before production use.
