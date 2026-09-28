# Engineering instructions

Treat this repository as a completely independent application. Do not read from,
write to, import from, migrate from, or make runtime assumptions about another
private application unless the owner explicitly authorizes a future integration.

Read SPECIFICATION.md, docs/IMPLEMENTATION_STATUS.md, and the chosen ticket first.
Actual code and test evidence define implementation status. Never mark a vendor
connected because its name appears in the source registry. Never claim a model
worked merely because a fixture or mocked HTTP response passed.

Preserve original source records, source dates, speaker uncertainty, exact text,
record revisions, rights constraints, and provenance. A semantic match creates a
candidate, not a merged proposition or reused review. Never use party, ideology,
network reputation, or personal preference as truth evidence. Do not fabricate
statements or findings about real people in fixtures.

Changes to foundational evidence invalidate downstream findings. Tests must cover
hard negatives as well as happy paths. Run pytest, schema regeneration/diff, the
standalone guard, and relevant integration checks. State what was not executed.
Do not weaken a gate or broaden access to turn a failed test green. No credentials,
licensed media, source corpora, model weights, or user database in Git.

## Acceleration-specific invariants

Only accepted, current, permissioned turns train speaker profiles. Original events, not
reposts, are the unit of feature support. Never train from a profile's own candidates.
Shadow mode defaults to all audio; low-scoring windows remain unprocessed, not absent.
Scope compatibility must preserve negation, date, geography, quantity and definitions.
Jev scores are uncalibrated routing features; backend failure cannot become no/false.
Capture provider bytes before validation; fixed endpoint and source egress grants apply.
Keep every claim card current against its reviews, source rights, expiry and corrections.
Run regression tests for migrations, cache invalidation and end-to-end selective media.
