FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN groupadd --gid 10001 ledger && useradd --uid 10001 --gid ledger --create-home ledger
WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN python -m pip install --no-cache-dir . && mkdir -p /data && chown ledger:ledger /data
USER ledger
ENV SL_DB_PATH=/data/ledger.sqlite3
EXPOSE 8765
CMD ["statement-ledger", "serve", "--host", "0.0.0.0", "--port", "8765"]
