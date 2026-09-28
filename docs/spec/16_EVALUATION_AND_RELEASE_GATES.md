## 16. Evaluation, acceptance criteria, and release gates

### 16.1 Evidence levels

Separate schema/unit proof, source-shaped fixture proof, mocked protocol proof, live API
proof, authorized media proof, human-labeled model evaluation, deployment proof, and
production observation. The validation report must identify which level supports each
claim. Passing a parser fixture does not prove source coverage. Passing a mocked speech
adapter does not prove transcription accuracy. Passing the synthetic duplicate example
does not establish robust deduplication across edited broadcasts.

All evaluation fixtures must be synthetic or explicitly permitted. Real-person labels
and findings require traceable source evidence. Do not fabricate a benchmark about a
named subject to make the repository appear complete. Hold out programs, time periods,
channels, and recording conditions from development where possible.

### 16.2 Required test categories

Contract tests cover record shapes, unknown fields, timezone/interval validity, expected
revisions, source parser mappings, source date semantics, pagination, repeated cursors,
response limits, credentials, and schema drift. Provenance tests cover missing/stale
parents, cycles, identity corrections, transcript revisions, rights expiry, evidence
scope, and audit consistency. Counting tests cover original/copy/replay distinctions,
repetition across different events, uncertain offsets, scope differences, and exclusions.
Security tests cover authentication, XSS-safe rendering, oversized requests, media path
boundaries, cross-workspace IDs in the target deployment, and restricted-source exports.

Media evaluation measures transcription error, word/segment timing error, diarization
error, speaker mapping errors, overlap handling, and performance by source condition.
Claim extraction evaluation measures grounding, speech act, atomicity, number/negation
preservation, scope completion, and abstention. Evidence review evaluation uses a
reviewer-authored rubric for applicability, cited-source correctness, handling of
counterevidence, and correction responsiveness. Human disagreement is recorded and
adjudicated, not hidden by collapsing to one unexplained label.

### 16.3 Proposed quality targets are not measured claims

For an initial reviewed pilot, require zero known wrong-person attributions among released
accepted turns and zero unsupported exact-quote spans. This is a release-blocking review
criterion, not a statistical guarantee about unreviewed material. Choose quantitative
model targets only after a representative baseline. Report numerators, denominators,
confidence intervals, source strata, and abstentions. A small clean sample cannot support
claims of near-perfect accuracy on all broadcasts.

The prototype's exact-coordinate deduplication must pass original/copy fixtures, while
edited/offset-drift cases remain explicitly unsupported until the alignment milestone.
For production counting, a curated hard-negative set must include the same words spoken
on different dates, a host quoting a guest, a montage, a replay, and two differently
bounded transcripts of the same utterance. No source-induced duplicate inflation is
acceptable in the released reviewed corpus.

### 16.4 Release gates

| Gate | Required evidence | Current meaning |
|---|---|---|
| G0: independent specification | Standalone contracts, source map, no external project dependency | Design and namespace guard |
| G1: local reference slice | Clean unit/API tests, synthetic demo, revision invalidation, clip utility proof | Shipped local proof |
| G2: real source contract | Authorized sample from each activated source; schema/permission receipt | Per-source access gate |
| G3: one-person private pilot | Permitted original/copy pair, reviewed speaker/context, sourced claims | Not yet completed |
| G4: robust media/occurrence linkage | Piecewise alignment, reversible equivalence, hard-negative tests | Planned |
| G5: assisted review workflow | Evaluated model proposals, reviewer UI, correction resolution | Planned |
| G6: production operations | Auth/RBAC, storage migration, isolated workers, budgets, retention, restore/load tests | Planned |
| G7: publication | Rights-complete snapshots, editorial approval, corrections/withdrawal | Planned; disabled |

The gates are cumulative for the relevant deployment. A source-specific feature may pass
its own G2 while another source remains blocked. No requirement says every commercial
provider must be purchased before useful private research; manual and open inputs can
prove the workflow. However, the product must not advertise an unactivated source as live.

### 16.5 Regression and reporting

Every bug fix adds a test that would have detected the error. Do not weaken correctness
gates to increase accepted volume. Re-run schema and openAPI generation after model or
route changes. Re-run the deterministic demo after every data-model change. Record the
Python/platform versions, dependency snapshot, commands, test results, optional skips,
source access, and current limitations. Maintain a machine-readable feature/status
manifest so a coding agent cannot infer completion from a document title or TODO stub.

The initial local validation report includes the executed synthetic tests and FFmpeg
clip test. Live source fetches and dependency locking encountered DNS failures in the
build environment. Provider credentials, speech model weights, Docker deployment, and
remote repository creation were not supplied or completed. These are explicit gates,
not silent assumptions hidden behind green unit tests.
