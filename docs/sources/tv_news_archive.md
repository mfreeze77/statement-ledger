# Internet Archive TV News Archive — source intake worksheet

Registry ID: `tv_news_archive`. Role: `transcript_discovery`. Access: `public_interface`.
Delivery state: **contract_only**. Live verification: **not performed**. This page is an integration contract and investigation plan, not proof of current account entitlement.

## Inputs and semantic mapping

Program title, network, broadcast date and time, archive item identifier, caption excerpt and preview offsets. Caption text is a lead for a spoken passage, not a verified utterance or speaker attribution.

Keep source-native IDs, original payload, parser version, retrieval time, and source grant. A quotation lead or media search match is not a confirmed appearance. Emit an `Observation` first; a reviewer or subsequently validated workflow establishes events, assets and exact utterances.

## Initial acquisition experiment

Search a bounded date range for a name and compare hits with the same program's official transcript; record caption lag, missing segments and preview limits. GDELT Television Explorer draws on this archive, so link rather than double-count a segment found through both.

Current next step: Capture a bounded caption-search sample and record which program, date and preview fields are actually returned.

Use a bounded sample, declared date range, page/byte limits, query fingerprint, and restart cursor. Save a receipt that distinguishes a genuinely empty permitted result from blocked access, parse failure, missing asset, expired link and exhausted page budget. Never expand scope or purchase access automatically.

## Rights and retention checklist

Record whether the granted operations cover metadata discovery, text retention, local audio processing, derivative clips, external-model transfer and publication. These permissions are independent. Record expiry and a source document or contract reference. A source's homepage or search availability is not a media reuse grant. Vendor samples must remain private unless their redistribution is explicitly authorized.

## Hard-negative test

A caption hit contains the subject's name spoken by a host introducing a segment the subject never appears in.

Also test missing required fields, repeated imports, source revisions, deleted links, uncertain dates and unexpected response shape. Parsing success does not establish factual accuracy or identity. An unsupported native response must fail explicitly rather than produce zero observations.

## Acceptance evidence

The connector graduate must supply the permitted sample hash, contract/documentation date, redacted fixture, parser mapping, test command/result, declared coverage and unresolved limitations. A registered source remains visible as blocked when access is unavailable. Claim no live support until a real bounded run has passed.

## Existing boundary

Closed-caption search and short previews locate broadcast segments; captions contain recognition errors and full-program access or reuse is restricted.

## Source references

- https://archive.org/details/tv

These are provider/documentation pointers. The status matrix and validation report, not the presence of a link, determine which integrations were exercised. Re-check dated articles and commercial terms before production use.
