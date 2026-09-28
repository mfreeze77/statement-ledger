"""Job identity excludes scheduling policy, never evidence or positional task inputs."""

from __future__ import annotations

from typing import Any

from statement_ledger.contracts.runtime import JobRequest


def job_content(request: JobRequest) -> dict[str, Any]:
    payload = request.model_dump(mode="json", exclude={"run_id", "max_attempts"})
    payload["inputs"] = sorted(
        payload["inputs"],
        key=lambda row: (row["kind"], row["id"], row["revision"], row["record_hash"]),
    )
    # Nested parameters belong to the handler contract. In particular, claim-matching
    # request.bindings and input_ids carry positional roles and must not be reordered.
    return payload
