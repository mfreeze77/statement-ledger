# First private person investigation

## 1. Create an isolated research workspace

Install and test the repository, then create a fresh database distinct from the synthetic demo:

```bash
statement-ledger --db data/research.sqlite3 seed-subject config/subject.scott-jennings.json
statement-ledger plan --person 'Scott Jennings' --out data/discovery-plan.json
```

The name is a search parameter, not a confirmed identity, appearance or allegation. Review aliases and public identity references before confirming media attribution. Do not infer private details or party beliefs from a name.

## 2. Fix the initial scope

Choose one dated public appearance as the initial end-to-end unit, with a declared source/date/channel collection around it. Keep every registry source visible, but execute only those whose access and budget have been approved. Record blocked subscriptions as gaps. Do not call the corpus complete because a query ended or a vendor returned no records.

## 3. Approve data use before retrieval

Read each source worksheet. Record a real `RightsGrant` for permitted operations. The synthetic rights example authorizes only synthetic demo material and must never be relabeled as a real-source permission. Create a real grant using the schema and retain the actual authorization reference. Metadata, text, media, processing, clipping, model transfer and publication are separate rights.

The v0.1 discovery CLI stores response files separately and is not an automatic rights/audit run manager. Review retention manually before invoking it and create appropriate coverage/observation records afterward. Full run reconciliation is a required next gate.

## 4. Run bounded discovery

```bash
statement-ledger discover --source youtube --query 'Scott Jennings' --pages 1 --out data/discovery/youtube
```

Supply `YOUTUBE_API_KEY` privately. Inspect the receipt and preserve its cursor. Search words appearing in a title can indicate only a discussion about the person. Use publisher transcripts, archive metadata, quote references and prior-review appearance links to corroborate and expand discovery. Do not use unapproved download tools for restricted media.

## 5. Ingest observations

After obtaining an authorized file/export and creating the relevant grant:

```bash
statement-ledger --db data/research.sqlite3 ingest \
  --source youtube --rights YOUR_REVIEWED_RIGHTS_ID \
  --file data/discovery/youtube/ACTUAL_RESPONSE_FILENAME.json --mode json
```

Use the actual emitted filename, not the receipt file. Treat an error receipt as partial failure. Review the normalized source observations. Do not promote quoted article text directly into an audiovisual utterance. Large root arrays require a conversion/staging workflow before they exceed the documented limit.

## 6. Establish the event and assets

Create an event supported by observations. Record the original broadcast date only when evidence supports it, otherwise leave it unknown. Confirm the person's appearance with rationale. Register original, copy and excerpt assets independently. A permitted local media file must match its Asset SHA-256 before processing. Align the source timeline to original-event time with explicit evidence; unresolved alignments remain uncountable.

## 7. Recover speech with context

Import a licensed transcript or run reviewed local speech models on approved bytes. Diarization supplies recording-local labels. Review at least the preceding question and subsequent clarification; enlarge windows when a statement crosses clip boundaries. Use the local model output as a candidate transcript, not unquestioned truth. For optional inference, first pin/install the model environment and benchmark the exact model revision; it was not executed for this delivery.

## 8. Resolve identity and exact words

Create confirmed speaker mappings only after evidence review. Correct mistaken transcript segments by writing a new transcript revision; dependent mappings and utterances must be revalidated. An accepted utterance must reproduce the exact selected segments. Keep overlap unresolved when attribution is not defensible. Unknown identity is a valid result.

## 9. Link scoped claims and evidence

Separate assertions, quotations, rejections, questions, hypotheticals, opinions and predictions. Create individual scoped propositions, then reviewer-approved occurrences. Prior fact-checks provide attributed research leads. Retain relevant primary evidence, exact excerpts, locators and time/geography/metric scope. A reviewed result requires its reviewer and limitations. No outcome is predetermined by the subject's identity.

## 10. Prove deduplication and correction behavior

Link a duplicate upload to the same event coordinates and show it does not increase original occurrences. Add a separate appearance asserting the same scoped proposition and show it can be a separate occurrence. Then revise one transcript/evidence parent and verify dependent results are marked stale. A correction record alone is not a corrected target revision.

## Exit criteria

Produce a private package with source/date coverage, confirmed and unresolved appearances, accepted utterances, external-review links, evidence-linked review records, duplicate groups, stale exclusions and correction history. A second reviewer must be able to reproduce an included record and explain a refused one. Do not publish or generalize a person's overall accuracy from this pilot.
