# Statement Ledger v0.2.0 — acceleration and shared research

This release extends the uploaded v0.1 package. It stays independent, preserves all 34
source registry entries/worksheets, and retains the original canonical evidence workflow.

## Added

A SQLite FTS5 claim index; bounded source-linked bulk claim seeds; topical claim families;
revision-bound review cards with expiry, scope and correction gates; deterministic
speaker phrase profiles; explicit incremental refresh; transcript-first candidate windows;
context padding and interval union; rejection audits; shadow/assist modes; combined
multi-person audio plans; the official optional TypeSafe Jev adapter; raw-before-parse
provider receipts; revision-aware caching; typed claim comparison; optional selective
media execution and acoustic similarity utility; calibration diagnostics and operator-priced
cost estimation; CLI/API entry points and three inspector views.

Six new specification chapters describe these systems, their invariants, examples,
acceptance criteria and remaining implementation boundaries. New runbooks cover migration,
a real localization experiment and building a source-linked claim library.

## Corrected

Provider configuration uses the official TypeSafe endpoint, not the unaffiliated endpoint
linked by the community article. Repeated uploads do not inflate language-profile event
counts. Speaker-language signals cannot create confirmed mappings. Provider failures do
not become negative answers. Independently quantized scores/probabilities are handled
with explicit compatibility warnings rather than silently discarded or renormalized.
Uncaptioned regions are not assumed silent. Open corrections block reuse candidates.
Legacy scope gaps remain unknown. An unrelated primary context excerpt no longer satisfies
the requirement for finding-relevant primary evidence. Audio-only clips no longer inherit
a video stream mapping. Per-window speaker labels and source offsets remain explicit.

## Not represented as finished

No real-person corpus or accusations are shipped. No live Jev inference, speech-model
accuracy benchmark, fitted identity calibrator, complete source harvesting, public
publishing, production tenancy or universal truth engine is claimed. Browser navigation
was attempted but may be blocked by this runtime; the validation report records the
actual result. The new local paths and mocked transports are tested separately.
