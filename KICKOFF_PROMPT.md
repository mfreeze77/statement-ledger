# Current agent entrypoint

Work from current main/PR state, not an old downloadable bundle. Read AGENTS.md and
`docs/runbooks/FOUNDATION.md` first. Run the locked baseline checks. Keep one module owner
per task and preserve schemas, hashes, immediate invalidation, rights and worker fences.
The product scope is unchanged; do not add more sources or product-spec chapters as setup.

# v0.2 next developer / coding-agent kickoff

Work only in this standalone repository. Read AGENTS.md, feature-status.json,
docs/IMPLEMENTATION_STATUS.md, docs/RELEASE_NOTES_V0_2.md and specification chapters 23–28.
The earlier 00–22 chapters and original tickets remain relevant; do not confuse historical
v0.1 limitation statements with current implemented capabilities.

Run the full suite, export schemas/OpenAPI, regenerate the combined specification, and run
the namespace guard. Run demo-acceleration in an empty database. Preserve exact-event copy
dedup and stale-dependency rejection from the old demo. Reproduce profiles, plans and claim
search before changing an algorithm. No fabricated real-person data is allowed.

The next release gate is real acceptance evidence, not another untested model wrapper.
Use authorized full-event media and captions with human labels. Train only on confirmed
turns, deliberately retain similar comparison speakers, and split evaluation by original
event across topics, sources and dates. Measure actual target-time/turn coverage and total
processing cost, including overlap, retries, screen calls and acoustic verification. Sample
low-scoring regions. Compare phrase-only, Jev-assisted and audio-first alternatives.

The optional provider must remain TypeSafe's official fixed endpoint. Never adopt the
separate service linked in a community blog. Pin a model, capture bytes before validation,
retain independently quantized numeric results without renormalizing, and distinguish a
backend fault from a semantic answer. Do not promote model confidence into identity
probability or automatically approve a finding. Use bounded paid calls only when authorized.

Select the smallest unmet ticket gate, record every executed command and actual dataset
rights/hash, and update release truth rather than changing mocks to conceal failure. Do not
activate other applications, share databases, remove source access gates or couple this
repository to private projects. Commit code, tests, documented limits and reproduction steps.
