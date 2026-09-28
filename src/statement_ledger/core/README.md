# Core invariants

Owns version checks, dependency edges, currentness, cycle rejection, rights and a sealed
validator registry. Concrete persistence is supplied by infrastructure; core cannot import
pillars or providers. Invalidation happens inside the source-change transaction; outbox
consumers only schedule subsequent work. Validators get read-only views, not writable SQL.
Run `uv run --locked pytest -q tests/test_domain.py tests/test_foundation.py` and `make check`.
