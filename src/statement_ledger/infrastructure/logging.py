"""Allowlisted structured diagnostics, separate from the canonical audit trail."""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import Any

SAFE_FIELDS = frozenset(
    {
        "run_id",
        "job_id",
        "attempt_id",
        "handler",
        "status",
        "error_code",
        "duration_ms",
        "sha256",
        "cost_status",
        "micro_usd",
    }
)


class SafeJSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        event = getattr(record, "event_code", "application.event")
        if not isinstance(event, str) or not event.replace(".", "").replace("_", "").isalnum():
            event = "application.event"
        payload: dict[str, Any] = {
            "at": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "event": event,
        }
        fields = getattr(record, "safe_fields", {})
        for key in SAFE_FIELDS:
            value = fields.get(key)
            if value is not None and isinstance(value, (str, int, float, bool)):
                payload[key] = value[:180] if isinstance(value, str) else value
        # Deliberately exclude record.msg, exception text, URLs, and provider request bodies.
        return json.dumps(payload, allow_nan=False, sort_keys=True)


def configure_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(SafeJSONFormatter())
    logger = logging.getLogger("statement_ledger")
    logger.handlers[:] = [handler]
    logger.propagate = False
    logger.setLevel(level)


def event(code: str, **fields: Any) -> None:
    logging.getLogger("statement_ledger").info(
        "", extra={"event_code": code, "safe_fields": fields}
    )
