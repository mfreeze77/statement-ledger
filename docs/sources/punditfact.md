# PunditFact — source intake worksheet

Registry ID: `punditfact`. Role: `review_discovery`. Access: `publisher_terms`.
Delivery state: **contract_only**. Live verification: **not performed**. This page is an integration contract and investigation plan, not proof of current account entitlement.

## Inputs and semantic mapping

Pundit-related review references and statement/source links; cross-link with the underlying publisher item.

Keep source-native IDs, original payload, parser version, retrieval time, and source grant. A quotation lead or media search match is not a confirmed appearance. Emit an `Observation` first; a reviewer or subsequently validated workflow establishes events, assets and exact utterances.

## Initial acquisition experiment

Deduplicate publisher identity while preserving distinct discovery paths and original review attribution.

Current next step: Link to canonical publisher review; trace its source broadcast.

Use a bounded sample, declared date range, page/byte limits, query fingerprint, and restart cursor. Save a receipt that distinguishes a genuinely empty permitted result from blocked access, parse failure, missing asset, expired link and exhausted page budget. Never expand scope or purchase access automatically.

## Rights and retention checklist

Record whether the granted operations cover metadata discovery, text retention, local audio processing, derivative clips, external-model transfer and publication. These permissions are independent. Record expiry and a source document or contract reference. A source's homepage or search availability is not a media reuse grant. Vendor samples must remain private unless their redistribution is explicitly authorized.

## Hard-negative test

The same review enters once via PunditFact and again via PolitiFact and becomes two independent reviews.

Also test missing required fields, repeated imports, source revisions, deleted links, uncertain dates and unexpected response shape. Parsing success does not establish factual accuracy or identity. An unsupported native response must fail explicitly rather than produce zero observations.

## Acceptance evidence

The connector graduate must supply the permitted sample hash, contract/documentation date, redacted fixture, parser mapping, test command/result, declared coverage and unresolved limitations. A registered source remains visible as blocked when access is unavailable. Claim no live support until a real bounded run has passed.

## Existing boundary

A PolitiFact collection; do not double-count a review discovered through both.

## Source references

- https://www.politifact.com/punditfact/

These are provider/documentation pointers. The status matrix and validation report, not the presence of a link, determine which integrations were exercised. Re-check dated articles and commercial terms before production use.
