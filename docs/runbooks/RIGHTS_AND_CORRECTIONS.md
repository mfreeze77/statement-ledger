# Rights, correction and incident handling

## New source or acquisition

Confirm the exact dataset/product and authorized operations. Store the actual source entitlement and review date. A template is not an entitlement. Keep approved hosts/endpoints fixed in connector code/configuration; do not fetch arbitrary URLs extracted from untrusted text. First retain a bounded permitted sample, then verify parser mapping and date semantics. External provider transfer requires explicit approval independent of local processing.

## Expired or revoked grant

Stop new acquisition/processing immediately. Expiry checks in v0.1 make dependent records ineligible when evaluated. That is not physical data removal. Inventory retained source files, derived clips, transcripts, indexes, backups and shared exports. Apply the contractual retention/delete process manually while the automated purge pipeline is pending. Preserve only legally permitted minimal audit metadata; do not use append-only design as a reason to retain prohibited personal or copyrighted material.

## Misattributed voice or wrong transcript

Freeze dependent outputs. Record the issue and its source reference. Write a corrected parent revision through the service with the current expected revision. Confirm downstream invalidation and inspect every affected utterance, occurrence and review. Reapproval requires renewed evidence, not a flag flip. Do not delete the historical explanation; if content retention is prohibited, apply a redaction/tombstone process under review.

## Reported correction

Record the correction as reported with its exact source, then independently confirm whether it addresses the original proposition. A later statement about a different period may not correct the earlier claim. A verified correction needs review. The current code records the correction and lists it with relevant dependencies; it does not automatically alter the target, repair counts or withdraw publication. Explicit target revision and downstream reconciliation are mandatory.

## Integrity mismatch or accidental exposure

Stop writers and exports, take a permitted forensic copy, rotate secrets, and compare with an independently stored backup. The local hash chain detects inconsistencies but is not tamper-proof against a database administrator. Preserve timestamps and actor details, enumerate impacted records, repair only through a documented process, and re-run integrity and reproduction checks. Do not claim trust restoration merely because the database opens.
