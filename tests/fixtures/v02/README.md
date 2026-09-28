# Frozen v0.2 migration input

`store.py.txt`, `jobs.py.txt`, and `util.py.txt` are unchanged UTF-8 source blobs from
`mfreeze77/statement-ledger` commit `ffcb18bca3b229772418c6fdb64087a3f161a54f`.
Their Git blob IDs are checked before execution in `tests/legacy_v02.py`.
The `.txt` suffix prevents the current formatter from rewriting this historical input;
these are ordinary readable source files, not encoded or compressed payloads.

The test loader supplies only the old Store's `models.now` import with a fixed UTC clock.
It does not import current models, current schema SQL or current migration helpers.
The old Store and JobQueue create WAL, schema_migrations version 2, FTS5, provider receipts
and an in-ledger jobs table. All generated records are fictional and created in pytest's
temporary directory. No binary database, credentials or real investigation is committed.
