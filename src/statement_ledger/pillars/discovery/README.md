# Discovery ownership

Consumes: Subjects, source contracts and permissioned inputs.

Produces/owns: Observations, leads, coverage and event/appearance resolution.

Use shared contracts and the core's read/dependency context; never import a sibling pillar
or a root compatibility facade. Application wires cross-owner workflows and validators.
No direct canonical writes in worker prepare functions. Changed inputs must invalidate
results before their transaction commits. Do not add a second source of truth.

Focused checks: `uv run --locked pytest -q tests/test_parsers.py tests/test_http.py`. Full gate: `make check`.
Model tests with fakes do not establish real-model accuracy; preserve evidence limitations.
