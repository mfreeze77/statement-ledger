# GDELT Global Quotation Graph — source intake worksheet

Registry ID: `gdelt_gqg`. Role: `quotation_discovery`. Access: `public_files`.
Delivery state: **file_parser**. Live verification: **not performed**. This page is an integration contract and investigation plan, not proof of current account entitlement.

## Inputs and semantic mapping

Article URL/title/language and date-seen field; each quote plus pre/post context; keep the original nested record.

Keep source-native IDs, original payload, parser version, retrieval time, and source grant. A quotation lead or media search match is not a confirmed appearance. Emit an `Observation` first; a reviewer or subsequently validated workflow establishes events, assets and exact utterances.

## Initial acquisition experiment

Import a small authorized historical window; quarantine unexpected nested shape and test duplicate re-import.

Current next step: Download an authorized dated .gqg.json.gz file, retain checksum, then ingest.

Use a bounded sample, declared date range, page/byte limits, query fingerprint, and restart cursor. Save a receipt that distinguishes a genuinely empty permitted result from blocked access, parse failure, missing asset, expired link and exhausted page budget. Never expand scope or purchase access automatically.

## Rights and retention checklist

Record whether the granted operations cover metadata discovery, text retention, local audio processing, derivative clips, external-model transfer and publication. These permissions are independent. Record expiry and a source document or contract reference. A source's homepage or search availability is not a media reuse grant. Vendor samples must remain private unless their redistribution is explicitly authorized.

## Hard-negative test

Two different speakers have the same quoted words; article-date-seen is not speech date.

Also test missing required fields, repeated imports, source revisions, deleted links, uncertain dates and unexpected response shape. Parsing success does not establish factual accuracy or identity. An unsupported native response must fail explicitly rather than produce zero observations.

## Acceptance evidence

The connector graduate must supply the permitted sample hash, contract/documentation date, redacted fixture, parser mapping, test command/result, declared coverage and unresolved limitations. A registered source remains visible as blocked when access is unavailable. Claim no live support until a real bounded run has passed.

## Existing boundary

Nested quotations with context; no automatic speaker confirmation.

## Source references

- https://blog.gdeltproject.org/announcing-the-global-quotation-graph/

These are provider/documentation pointers. The status matrix and validation report, not the presence of a link, determine which integrations were exercised. Re-check dated articles and commercial terms before production use.
