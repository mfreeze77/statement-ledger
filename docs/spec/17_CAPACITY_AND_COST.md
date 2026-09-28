## 17. Capacity planning, costs, and operating budgets

### 17.1 Workload variables

Define `A` as original audio/video hours acquired, `D` as distinct hours after asset
reconciliation, `P` as processed hours, `T` as accepted target-speaker hours, `U` as exact
utterances, `C` as candidate claims, and `R` as reviewed propositions. Keep these separate:
a mirrored clip can increase acquired bytes without increasing original hours or claims.
A failed diarization pass can increase compute without increasing accepted turns.
Operational reports need both useful output and failed/repeated work.

Metadata work is measured in requests, pages, results, and bytes per source. Source costs
may depend on request, mention, transcript, recording hour, historical backfill, seat,
or contract. Do not hard-code a universal quota or monthly price from an old overview.
Each activated source gets a current configured cost model and an explicit budget.

### 17.2 Storage estimates as formulas

For constant media bitrate `b` megabits per second, decimal storage per hour is
`b × 3600 / 8 / 1000` gigabytes, or `0.45 × b` GB/hour. Thus an illustrative 2 Mb/s copy
occupies about 0.9 GB per hour before container, metadata, replicas, and filesystem
overhead. This is an arithmetic example, not a measured source bitrate. Audio at 64 kb/s
is approximately 28.8 MB/hour. Actual sources must be probed and measured.

Storage planning includes originals, derived audio, retained context clips, transcripts,
raw source files, indexes, revision history, backups, and temporary worker output.
Set retention separately per asset class. A duplicate media hash may permit deduplicated
storage within an allowed rights boundary, but do not collapse distinct source metadata
or assume two customer licenses allow shared retained objects.

### 17.3 Compute and model usage

Let `f_asr` be measured compute-seconds per audio-second for a chosen model/hardware/config.
ASR compute hours are approximately `P × f_asr`, before retries and preprocessing.
Diarization, alignment, and video analysis need their own factors. A publisher's reported
speedup is not a planning guarantee. Benchmark representative recordings, including long
panels and overlap, and reserve headroom for failures and reprocessing after corrections.

For a generative-model stage, cost is `input_tokens × input_unit_price + output_tokens ×
output_unit_price`, plus any tool or hosting charges. Cache reuse reduces calls only when
all relevant input/model/rights revisions match. Count rejected or malformed responses as
costs, not as zero-cost successful reasoning. A cheap routing model can reduce expensive
analysis only if its missed-candidate rate is acceptable on the evaluation corpus.

### 17.4 Human-review capacity

Human review is often the pacing constraint. Measure minutes to resolve an appearance,
map a speaker, accept a contextualized utterance, review a claim, and resolve a correction.
Separate straightforward confirmations from difficult cases. The interface should reduce
repetitive work by presenting source context and prior compatible research, not by
encouraging acceptance without evidence. Review throughput is a measured operational
quantity, not a reason to weaken the inclusion rules.

### 17.5 Budget enforcement

The target budget ledger reserves spend or units before dispatch and reconciles actual
usage after completion. It has separate caps for source requests, acquired bytes, media
hours, model tokens, worker time, and review workload. A task that exceeds its budget
pauses with a saved cursor/result receipt. It does not silently drop material and mark
the run complete. A retry shares a logical task budget but records each physical attempt.
Reconciliation releases unused reservations and handles crash recovery explicitly.

The reference CLI offers page and record limits but does not implement a financial budget
reservation service. Large paid crawls are therefore not enabled. Begin with a bounded
authorized pilot, measure actual resource usage, then set the capacity and cost envelope.
