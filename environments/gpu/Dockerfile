ARG UV_IMAGE=ghcr.io/astral-sh/uv:0.9.21@sha256:15f68a476b768083505fe1dbfcc998344d0135f0ca1b8465c4760b323904f05a
ARG GPU_PYTHON_IMAGE=python:3.11-slim-bookworm@sha256:a36c24f9cbdf4fd0f52d67f0823eeac19c2028c637cecc392d97f980d4fec56b
FROM ${UV_IMAGE} AS uv
FROM ${GPU_PYTHON_IMAGE}
COPY --from=uv /uv /uvx /bin/
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg ca-certificates && rm -rf /var/lib/apt/lists/*     && groupadd --gid 10001 ledger && useradd --uid 10001 --gid ledger --create-home ledger
WORKDIR /workspace
COPY pyproject.toml uv.lock README.md LICENSE ./
COPY src ./src
COPY environments/gpu ./environments/gpu
ENV UV_PROJECT_ENVIRONMENT=/opt/gpu UV_CACHE_DIR=/tmp/uv-cache
RUN uv sync --project environments/gpu --locked --no-dev && mkdir -p /data && chown ledger:ledger /data
ENV PATH=/opt/gpu/bin:$PATH PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1     SL_DATA_ROOT=/data SL_DB_PATH=/data/db/ledger.sqlite3 SL_WORKER_CAPABILITY=gpu     LD_LIBRARY_PATH=/opt/gpu/lib/python3.11/site-packages/nvidia/cublas/lib:/opt/gpu/lib/python3.11/site-packages/nvidia/cudnn/lib
USER ledger
CMD ["statement-ledger", "worker"]
