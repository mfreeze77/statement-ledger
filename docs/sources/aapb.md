# American Archive of Public Broadcasting — source intake worksheet

Registry ID: `aapb`. Role: `archive_discovery`. Access: `public_metadata_restricted_transcripts`.
Delivery state: **http_client**. Live verification: **not performed**. This page is an integration contract and investigation plan, not proof of current account entitlement.

## Inputs and semantic mapping

GUID/item ID, public metadata, collection references, transcript availability, timed text only after approved access.

Keep source-native IDs, original payload, parser version, retrieval time, and source grant. A quotation lead or media search match is not a confirmed appearance. Emit an `Observation` first; a reviewer or subsequently validated workflow establishes events, assets and exact utterances.

## Initial acquisition experiment

Validate one real metadata response and separately request transcript access; keep missing transcripts explicit.

Current next step: Use metadata client; request transcript credentials and capture actual samples.

Use a bounded sample, declared date range, page/byte limits, query fingerprint, and restart cursor. Save a receipt that distinguishes a genuinely empty permitted result from blocked access, parse failure, missing asset, expired link and exhausted page budget. Never expand scope or purchase access automatically.

## Rights and retention checklist

Record whether the granted operations cover metadata discovery, text retention, local audio processing, derivative clips, external-model transfer and publication. These permissions are independent. Record expiry and a source document or contract reference. A source's homepage or search availability is not a media reuse grant. Vendor samples must remain private unless their redistribution is explicitly authorized.

## Hard-negative test

Catalog entry exists but no transcript is available; metadata response is not silently treated as empty speech.

Also test missing required fields, repeated imports, source revisions, deleted links, uncertain dates and unexpected response shape. Parsing success does not establish factual accuracy or identity. An unsupported native response must fail explicitly rather than produce zero observations.

## Acceptance evidence

The connector graduate must supply the permitted sample hash, contract/documentation date, redacted fixture, parser mapping, test command/result, declared coverage and unresolved limitations. A registered source remains visible as blocked when access is unavailable. Claim no live support until a real bounded run has passed.

## Existing boundary

Public metadata; transcript API needs research credentials; schema is experimental.

## Source references

- https://github.com/WGBH-MLA/AAPB2

These are provider/documentation pointers. The status matrix and validation report, not the presence of a link, determine which integrations were exercised. Re-check dated articles and commercial terms before production use.
