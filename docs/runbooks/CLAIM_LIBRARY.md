# Build and inspect the shared claim library

All original source connectors remain inputs. Their observations become leads, not truth
labels. The existing general `ingest` command preserves native sources. The new
`seed-claims` command handles a deliberately narrow interchange after authorized source
transformation.

Example `seeds.jsonl` row:

```json
{"native_id":"publisher-record-123","source_url":"https://example.org/original","claim_text":"An exact claim to investigate.","scope":{},"attributed_to":"Publisher-reported speaker"}
```

```bash
statement-ledger --db data/ledger.sqlite3 seed-claims --file seeds.jsonl.gz --source manual_import --rights YOUR_RIGHTS_ID --max-records 10000
statement-ledger --db data/ledger.sqlite3 search-claims "claim wording"
```

The source ID must match the grant. No grant is supplied for arbitrary internet content.
Gzip/bzip2 are optional. The original file is retained. Every accepted seed is ambiguous
until reviewed; it creates no speaking occurrence and no finding. Per-row errors are
reported, not discarded. `bounded_or_eof` means the file limit may have been reached.

Use `put proposition` to record reviewed scope, and the ordinary utterance/occurrence/
evidence/review workflow to establish source-bound assertions and findings. A claim card
references completed reviews; its expiry and rationale are explicit. Existing source
reviews are research aids, not the application's own automatically accepted verdicts.

```json
{
  "id":"card-example", "proposition_id":"reviewed-proposition",
  "review_ids":["reviewed-evidence-record"],
  "valid_until":"2027-01-01T00:00:00+00:00",
  "freshness_rationale":"Replace with a real domain-specific expiry justification.",
  "approved_by":"authenticated operator's recorded review identity"
}
```

The example date is illustrative, not a recommended universal expiry. The record must
reference real current reviews. Inspect `/api/claims/cards/CARD_ID` for conflicts, missing
scope, open corrections and expired dependencies. No endpoint silently copies a verdict
onto a new speaker's statement.

An optional typed comparison can be run after enabling Jev:

```bash
statement-ledger --db data/ledger.sqlite3 match-claims NEW_PROPOSITION CANDIDATE_1 CANDIDATE_2
```

It returns model proposals plus deterministic scope gates. The raw receipts and bindings
remain in the private database. A family groups related propositions for navigation but
cannot approve equivalence. Human review still determines whether prior research applies.
