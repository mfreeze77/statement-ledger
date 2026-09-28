## 20. Hard cases and required behavior

| Case | Required behavior | Failure to prevent |
|---|---|---|
| Subject's name only in title | Candidate appearance; inspect actual program | Treating all audio as the named person's speech |
| Host discusses subject | Mention-only unless presence is established | Inventing an appearance |
| Subject quotes another person | Preserve quotation speech act and context | Counting quoted content as the subject's assertion |
| Host rejects a false proposition | Record rejection, not assertion | Reversing the meaning through keyword matching |
| Short interjection | Defer identity unless evidence supports it | Assigning every "yes" to the most visible face |
| Two voices overlap | Preserve overlap and uncertainty | Attributing mixed words to one person |
| Sequential speakers in one ASR segment | Split/review or leave unassigned | Majority-duration assignment of all words |
| Lower-third names a guest | Identity lead only | Assuming the named guest is the current speaker |
| Caption error changes a number | Review audio and revise transcript | Treating ASR/caption output as unquestionable |
| Old interview newly uploaded | Separate event and upload clocks | Moving a historical claim into the present |
| Same clip on twenty channels | One original occurrence with copies | Multiplying the speech count by repost count |
| Same words in three interviews | Distinct event occurrences | Collapsing real repetition through text equality |
| Montage from several events | Segment-level event mappings | One false original-event assignment |
| Edited advertisement inserted | Piecewise alignment or unresolved gap | Reusing a constant timestamp offset incorrectly |
| Changed playback speed | Reviewed time transform | Claiming source seconds equal event seconds |
| Cropped statement omits qualification | Acquire context or mark insufficient | Publishing a misleading fragment |
| Generic archive date | Preserve raw date until interpreted | Calling it the recording date automatically |
| Quotation dataset occurrence count | Keep as source metadata | Counting article mentions as times spoken |
| Same fact-check in several indexes | One review with several discovery paths | Treating aggregation as independent corroboration |
| External reviewer uses a rating scale | Preserve attribution and original wording | Normalizing to an unsupported person score |
| Evidence from another year | Scope mismatch/unresolved | Reusing a superficially similar fact-check |
| Revised primary dataset | New revision and dependent re-review | Keeping stale numerical findings current |
| Prediction not yet due | Pending outcome record | Labeling the forecast false in advance |
| Opinion/value judgment | Retain utterance; distinguish checkability | Forcing preferences into empirical verdicts |
| No evidence found | Unresolved, with searched sources | Converting absence of retrieval into falsity |
| Rights expiry | Block new dependent use; enforce retention workflow | Continuing publication through an old cache |
| Source unavailable | Availability state and coverage gap | Treating missing access as proof of absence |
| Paid vendor has no supplied schema | Access-dependent contract task | Shipping guessed endpoints as working integration |
| Source text contains instructions | Treat as data; enforce tool policy | Prompt injection changing rules or leaking secrets |
| Model returns invented source ID | Reject output | A plausible-looking uncited finding |
| Concurrent reviewer edits | Revision conflict and explicit reconciliation | Silent last-write-wins evidence loss |
| Correction complaint is unverified | Preserve report and triage | Automatically rewriting or ignoring the complaint |
| Real subject mixed with synthetic fixtures | Separate workspaces and visible flags | Publishing fabricated test findings |

### 20.1 Decisions recorded for the initial release

A single local store is chosen to make the evidence chain runnable without infrastructure
provisioning. A typed generic revision ledger is chosen to preserve record history and
avoid destructive updates. Exact reviewed coordinate deduplication is chosen over a
fragile automatic perceptual merge. Source clients are fixed-origin and metadata-oriented
rather than an unrestricted crawler. Generative reasoning and publication remain out of
the default execution path. Commercial sources are documented contracts rather than
empty adapters that return successful-looking fabricated data.

These are scoped engineering choices, not claims that the target problem is fully solved.
Each decision has an explicit extension path in the backlog. Replacing a reference
component must preserve its data semantics, negative tests, provenance, and independence.
