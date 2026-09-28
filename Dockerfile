# Image references are resolved to immutable digests in containers/images.json.
ARG UV_IMAGE=ghcr.io/astral-sh/uv:0.9.21@sha256:15f68a476b768083505fe1dbfcc998344d0135f0ca1b8465c4760b323904f05a
ARG PYTHON_IMAGE=python:3.13-slim-bookworm@sha256:2325bb286ec344af3e5898cc224b5844e2707ac6e26b1632516fd3edc84a5e26
FROM ${UV_IMAGE} AS uv
FROM ${PYTHON_IMAGE} AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 UV_PROJECT_ENVIRONMENT=/opt/venv UV_CACHE_DIR=/tmp/uv-cache
COPY --from=uv /uv /uvx /bin/
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg git ca-certificates make && rm -rf /var/lib/apt/lists/*     && groupadd --gid 10001 ledger && useradd --uid 10001 --gid ledger --create-home ledger
WORKDIR /workspace
COPY pyproject.toml uv.lock README.md LICENSE ./
COPY src ./src
FROM base AS dev
RUN uv sync --locked --group dev && mkdir -p /data && chown ledger:ledger /data
COPY . .
ENV PATH=/opt/venv/bin:$PATH SL_DATA_ROOT=/data SL_DB_PATH=/data/db/ledger.sqlite3
USER ledger
CMD ["statement-ledger", "doctor"]
FROM base AS runtime
RUN uv sync --locked --no-dev --no-editable && mkdir -p /data && chown ledger:ledger /data
ENV PATH=/opt/venv/bin:$PATH SL_DATA_ROOT=/data SL_DB_PATH=/data/db/ledger.sqlite3 SL_HOST=0.0.0.0
USER ledger
EXPOSE 8765
CMD ["statement-ledger", "serve"]
