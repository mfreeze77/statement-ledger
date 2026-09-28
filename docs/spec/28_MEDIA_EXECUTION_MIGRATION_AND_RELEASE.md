## 28. Local media execution, additive migration and v0.2 release boundary

### 28.1 Selective media execution

`process-localization` accepts a current localization-run ID, a local media file, a new
output directory and an allowed media root. It validates the file checksum against its
asset, checks current provenance and permissions, and creates only the run's selected
intervals. Shadow plans therefore process the entire recording; assist plans process
the proposed smaller workload. Both input and output must resolve inside the allowed
root. The source is never overwritten and an existing output directory is refused.

The command writes a manifest before work begins and updates it after each completed
clip. On failure it leaves a failed manifest and the completed items for inspection.
There is no hidden automatic resume that could confuse old results with a changed source.
FFmpeg re-encodes rather than pretending keyframe-only copying is exact. Audio-only M4A
or WAV destinations no longer inherit a video mapping. Each real clip is probed and a
large duration mismatch stops processing.

### 28.2 Coordinate discipline

A media result retains clip-relative coordinates and the source start offset. Derived
segment and diarization-turn metadata also carry source-coordinate fields. Local speaker
labels are prefixed by the window ID; `speaker_0` in a later crop is not assigned to the
same person by name equality. These outputs remain candidates and are not automatically
imported as accepted utterances.

The first implementation validates requested interval bounds and clip duration. It does
not certify codec sample-exact alignment, automatically reconcile words that cross a
crop boundary, or verify every model timestamp against the waveform. Forced alignment,
source-coordinate word indexing, edited-compilation mapping and cross-window acoustic
clustering remain separately evaluated work. The manifest makes that boundary visible.

### 28.3 Optional acoustic comparison

`speech.verify_speaker_clips` wraps a pre-provisioned local SpeechBrain ECAPA model. It
requires local clip files, a pinned model-directory revision and explicit audio/biometric
processing permissions. It returns cosine similarity and file hashes, not a named-person
identity probability. The model's binary prediction is not used to approve a mapping.
No weights are bundled and the function does not download a model on its own.

The operator must select suitable reference and candidate clips and establish their
source provenance. The utility itself does not prove who is in the enrollment recording.
Replay, impersonation, overlap, short clips and cross-channel recording differences are
review concerns. Local file and permissions checks are implemented; live model inference
was not run in this release. Consult the primary [SpeechBrain model card](https://huggingface.co/speechbrain/spkrec-ecapa-voxceleb)
for the inference interface and its stated out-of-domain limitations.

### 28.4 Database upgrade and rollback

The v0.2 store creates an FTS projection, provider-receipt storage, migration tracking
and lookup indexes. Original record revisions, hashes and audit history are not rewritten
merely to add missing optional fields. A native SQLite backup must be taken with the old
application stopped or through its online-backup command before first opening the real
workspace in the new version. Run integrity checks before and after the upgrade.

New Scope fields default to unknown when reading legacy data. They are not silently
filled with `not_applicable`. Old cards/claims may consequently fail new reuse-candidate
checks until reviewed. Historical source records remain inspectable. Updating a legacy
record creates a normal new revision with the expanded schema and expected-revision guard.

Rollback restores the pre-upgrade database backup and the previous code together. Do not
run old code against new extension records and assume it understands them. Preserve the
v0.2 database separately before rollback so new research is not silently lost. JSON
exports are private inspection backups; native SQLite backup is the tested complete
workspace copy, including receipt tables. Generated search indexes are rebuildable.

### 28.5 Security and retention

The application remains an authenticated single-owner research workspace. No deployment
or credentials are borrowed from another project. The expanded API exposes profile
build/refresh, local plan generation, claim search/card inspection and explicitly enabled
Jev analysis. Browser credentials stay in memory, never browser persistent storage.
Expensive local media processing remains a CLI operation rather than accepting arbitrary
server paths from browser requests.

Provider receipts may contain licensed transcript text. Configure retention and deletion
before operational use; this release does not implement an autonomous purge daemon or
claim cryptographic erasure from backups. Rights expiration blocks new processing and
reuse, but does not automatically delete every retained copy. Such deletion requires an
operator-managed retention workflow and backup policy. No third-party media or biometric
reference recordings are bundled.

### 28.6 Scope of delivery

The upgrade implements local claim indexing/bulk seeding, evidence-card freshness and
correction gates, reproducible language profiles, explicit profile refresh, transcript
window planning, audits/fallbacks, an optional typed decision adapter/cache, selective
local media execution, advisory local speaker comparison, evaluation diagnostics, cost
calculation, CLI/API entry points and inspector views. It preserves all original named
source worksheets and connector contracts.

Not delivered as completed capabilities: licensed access to all sources, full web/video
harvesting, a complete corpus of real pundit statements, an automatically fitted speaker
classifier, full production search at unbounded scale, autonomous fact adjudication,
intent detection, universal person scores, public publishing or unattended deployment.
The distinction is enforced by default modes and record contracts, not only prose.

### 28.7 Verification record

Use `docs/VALIDATION_REPORT.md` and machine-readable files under `validation/` for the
actual release results. A successful mock validates client behavior, not the provider's
real latency or accuracy. A successful synthetic audio clip validates the execution
path, not real panel-discussion diarization. A blocked browser navigation is not a visual
pass. The release process records these limits rather than converting missing tests into
claims of completion.


JSON backup version 2 encodes provider receipt bytes as `body_base64` so even malformed non-UTF-8 responses survive export exactly. The native SQLite backup remains the supported database-restore mechanism; JSON export is inspectable interchange, not an implemented automatic restore command.
