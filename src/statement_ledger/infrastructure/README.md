# Infrastructure boundaries

Owns concrete SQLite/migrations, named secrets/settings, immutable local artifacts, queue,
worker, operation receipts and optional provider implementations. It imports contracts/core,
not application or pillars. The application supplies typed handlers and validators.
Heavy work runs outside DB transactions; accepted effects require a live lease and current
inputs. SQLite and its named Docker volume stay on one host. Model weights are never built
into images. Run `uv run --locked pytest -q tests/test_foundation.py tests/test_foundation_execution.py`.
