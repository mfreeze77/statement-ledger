# Reviewed synthetic-hash detections

The Phase 0 history scan at `7e6dedc1` reported three `generic-api-key` findings in
`proof/synthetic-demo.json`, introduced by `ffcb18b`. Lines 24 and 99 contain the
same original-event deduplication identifier; line 174 contains the repeat-event
identifier. These values are not credentials. The file is entirely fictional.

The test `test_allowlisted_values_are_reproducible_event_ids` independently
reproduces each SHA-256 from compact JSON containing event ID, fictional person
ID, proposition ID, start and end milliseconds. No secret input is involved.

The exception extends only the default `generic-api-key` rule. It requires both
that exact path and a complete JSON line containing `canonical_key` with one of
the two reviewed values. It does not suppress commits, directories, other fields,
other hashes or GitHub/provider credential rules. Default Gitleaks rules remain on.

The prior scanner self-test used a repeated-X token-shaped marker below the
pinned detector's entropy floor of 3. It could not prove that the detector worked.
The revised test constructs a varied, non-issued marker at runtime. It never
contacts a credential service, logs the marker or commits it to this repository.

`python scripts/secret-scan-proof.py` runs the pinned scanner with the actual
project configuration against five temporary cases: the reviewed fixture, a
synthetic PAT in the same file, a different canonical value, a different path,
and a different field. The first must be clean and all four positive controls
must be detected by their expected rules. Report and output redaction is checked;
scanner errors, timeouts and malformed/missing reports fail closed. Scan inputs
are read-only and networking is disabled inside each scanner container.

Unit tests additionally exercise failure/redaction cases and the exception's
path/value/field specificity. CI remains a blocking full-history scan; this is
false-positive remediation, not disabling a security gate.

Upstream reference: https://github.com/gitleaks/gitleaks/blob/v8.24.2/README.md
Default detector: https://github.com/gitleaks/gitleaks/blob/v8.24.2/config/gitleaks.toml
