# First transcript-first localization experiment

Use a separate research workspace with authorized media. Start from confirmed accepted
turns, not passages predicted by this same system. Select comparison speakers explicitly.
Reserve whole events for evaluation and include hard negatives from similar programs.

## Create and refresh a profile

Create `profile-input.json` using real existing record IDs:

```json
{
  "person_id": "your-person-id",
  "example_ids": ["accepted-target-turn-1", "accepted-target-turn-2"],
  "background_ids": ["accepted-other-turn-1", "accepted-other-turn-2"],
  "profile_id": "profile-your-person",
  "config": {"min_events": 2, "min_background_events": 2}
}
```

```bash
statement-ledger --db data/ledger.sqlite3 build-profile profile-input.json
statement-ledger --db data/ledger.sqlite3 refresh-profile profile-your-person --holdout-event evaluation-event
```

The example IDs are placeholders, not bundled real evidence. All relevant grants need
`learn_profile`. Review the resulting independent event counts and supported phrases.
`research_ready` is only minimum sample readiness. Unknown or stale inputs cannot train.

## Plan before processing

```json
{
  "profile_id": "profile-your-person",
  "transcript_id": "your-timestamped-transcript",
  "config": {
    "mode": "shadow", "window_ms": 30000, "stride_ms": 15000,
    "padding_ms": 10000, "audit_fraction": 0.1
  }
}
```

Save this as `localize-input.json`:

```bash
statement-ledger --db data/ledger.sqlite3 localize localize-input.json --out plan.json
```

Inspect proposed versus selected intervals, caption gaps and fallback reasons. Run shadow
processing to get an unbiased view of excluded audio before moving to assist. A low score
never records target absence. Add `--jev` only after provider configuration and source
submission permissions are established. Typed answers are retained separately from identity.

## Process only the plan's selected regions

```bash
statement-ledger --db data/ledger.sqlite3 process-localization RUN_ID \
  --input media/original.mp4 --output-dir media/derived/run-001 --root media
```

The input must match the asset's registered SHA-256. The destination must not exist.
FFmpeg/ffprobe are required. Add `--transcribe` and/or `--diarize` only in an environment
with the optional speech libraries, weights and applicable terms. The command leaves a
manifest with offsets and failure status. Labels remain local to each clip and identities
remain unconfirmed. Inspect outputs before importing any derived transcript.

## Evaluate the selection

A label file names the exact asset and independent target turns:

```json
{"asset_id":"your-asset-id","truth_complete":true,"target_intervals":[{"start_ms":100000,"end_ms":110000}]}
```

```bash
statement-ledger --db data/ledger.sqlite3 evaluate-localization RUN_ID labels.json
```

Only set `truth_complete` after reviewing the whole relevant recording. Compare phrase
only, phrase-plus-Jev and audio-first alternatives on identical held-out events. Keep
uncertain labels and failure costs visible. No command in this release auto-promotes a
threshold or automatically names a person from a language pattern.
