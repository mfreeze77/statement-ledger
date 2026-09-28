"""Optional TypeSafe Jev transport with raw capture, strict contracts and explicit faults.

The endpoint is deliberately fixed to the official provider. The community article's
unaffiliated endpoint is NOT used. No secrets or caller-selected URLs enter state.
"""

from __future__ import annotations

import json
import math
import time
import uuid
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import Any

import httpx

from statement_ledger.contracts.models import RightsGrant, now
from statement_ledger.core.policy import PolicyError, require_right
from statement_ledger.core.read import current
from statement_ledger.core.util import canonical_json, digest

ENDPOINT = "https://api.typesafe.ai/v1/systemone"
DEFAULT_MODEL = "jev-1.13.0"
VALIDATOR_VERSION = "typesafe-contract-v2"
MAX_RESPONSE_BYTES = 512 * 1024


@dataclass(frozen=True)
class JevConfig:
    model: str = DEFAULT_MODEL
    timeout_seconds: float = 20.0
    max_attempts: int = 3
    max_request_bytes: int = 64000
    max_retry_seconds: float = 30.0
    cache_seconds: int = 86400

    def __post_init__(self):
        if not self.model.startswith("jev-"):
            raise ValueError("Expected a Jev model identifier")
        if not 1 <= self.max_attempts <= 5 or not 0 < self.timeout_seconds <= 120:
            raise ValueError("Invalid request limits")
        if not 1024 <= self.max_request_bytes <= 200000 or not 0 <= self.max_retry_seconds <= 120:
            raise ValueError("Invalid size/retry limits")
        if not 0 <= self.cache_seconds <= 604800:
            raise ValueError("Invalid cache TTL")


def cache_eligible(
    payload: Mapping[str, Any], config: JevConfig, *, at: datetime | None = None
) -> bool:
    """Shared policy for canonical and recovered results. Never refresh capture time on reuse."""
    if (
        config.model in {"jev-latest", "jev-preview"}
        or payload.get("model_requested") != config.model
        or payload.get("status") != "available"
    ):
        return False
    try:
        captured = datetime.fromisoformat(payload["captured_at"])
        age = ((at or now()) - captured).total_seconds()
    except (KeyError, TypeError, ValueError, OverflowError):
        return False
    return 0 <= age < config.cache_seconds


def find_cached_decision(
    ledger: Any, request_hash: str, config: JevConfig
) -> dict[str, Any] | None:
    for row in ledger.store.find_decisions(request_hash):
        if cache_eligible(row["payload"], config) and ledger.dependencies_current(
            "decision_run", row["id"]
        ):
            return row
    return None


class ResponseContractError(ValueError):
    pass


def strict_loads(body):
    def obj(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise ResponseContractError("duplicate_json_key")
            out[key] = value
        return out

    def constant(value):
        raise ResponseContractError("nonfinite_json_number")

    try:
        return json.loads(body, object_pairs_hook=obj, parse_constant=constant)
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise ResponseContractError("invalid_json") from e


def number(value, low, high):
    if type(value) not in (int, float) or not math.isfinite(value) or not low <= value <= high:
        raise ResponseContractError("numeric_range_or_type")
    return float(value)


def validate_questions(questions):
    if not isinstance(questions, dict) or not 1 <= len(questions) <= 64:
        raise ValueError("Questions must contain 1..64 items")
    for key, q in questions.items():
        if (
            not isinstance(key, str)
            or not key
            or not isinstance(q, dict)
            or not q.get("instructions")
        ):
            raise ValueError("Question ID and instructions required")
        if set(q) - {"type", "instructions", "criteria"}:
            raise ValueError("Unknown question fields")
        kind = q.get("type")
        criteria = q.get("criteria")
        if kind == "choice" and (not isinstance(criteria, dict) or not 2 <= len(criteria) <= 255):
            raise ValueError("Choice requires criteria")
        if kind == "score" and (not isinstance(criteria, list) or not 2 <= len(criteria) <= 10):
            raise ValueError("Score requires ordered criteria")
        if (
            kind == "noul"
            and criteria is not None
            and (not isinstance(criteria, dict) or set(criteria) != {"true", "false"})
        ):
            raise ValueError("Noul criteria must be true/false")
        if kind not in {"choice", "score", "noul"}:
            raise ValueError("Unknown question type")


def validate_response(raw, questions, model):
    """Do not recompute confidence or require exact score=rounded expectation.

    Official examples expose probability distributions; observed provider quantization
    requires narrowly bounded compatibility, NOT normalization or arbitrary tolerance.
    """
    if not isinstance(raw, dict) or not isinstance(raw.get("model"), str):
        raise ResponseContractError("missing_model")
    if model not in {"jev-latest", "jev-preview"} and raw["model"] != model:
        raise ResponseContractError("resolved_model_mismatch")
    answers = raw.get("answers")
    if not isinstance(answers, dict) or set(answers) != set(questions):
        raise ResponseContractError("question_id_mismatch")
    warnings = []
    for key, q in questions.items():
        a = answers[key]
        if not isinstance(a, dict) or a.get("type") != q["type"]:
            raise ResponseContractError("answer_type_mismatch")
        if q["type"] == "noul":
            number(a.get("noul"), 0, 1)
            continue
        number(a.get("confidence"), 0, 1)
        expected = (
            set(q["criteria"])
            if q["type"] == "choice"
            else {str(i) for i in range(len(q["criteria"]))}
        )
        probs = a.get("probabilities")
        if not isinstance(probs, dict) or set(probs) != expected:
            raise ResponseContractError("probability_keys_mismatch")
        values = [number(p, 0, 1) for p in probs.values()]
        residual = abs(sum(values) - 1)
        quantized = all(abs(v * 100 - round(v * 100)) < 1e-7 for v in values)
        tolerance = 0.005 * len(values) + 1e-8 if quantized else 1e-6
        if residual > tolerance:
            raise ResponseContractError("invalid_probability_total")
        if residual > 1e-6:
            warnings.append(f"{key}:independent_2dp_probability_quantization")
        if q["type"] == "choice":
            choice = a.get("choice")
            if choice not in expected:
                raise ResponseContractError("unknown_choice")
            if max(values) - float(probs[choice]) > 1e-6:
                raise ResponseContractError("choice_not_argmax")
        else:
            score = number(a.get("score"), 0, len(expected) - 1)
            if not isinstance(a.get("legend"), dict) or set(a["legend"]) != expected:
                raise ResponseContractError("score_legend_mismatch")
            # Simple criteria must match their documented order. Structured criteria
            # are retained but descriptions are provider formatting, not inferred IDs.
            if all(isinstance(c, str) for c in q["criteria"]):
                if a["legend"] != {str(i): c for i, c in enumerate(q["criteria"])}:
                    raise ResponseContractError("score_legend_order")
            expectation = sum(int(k) * float(v) for k, v in probs.items())
            slack = 0.005 * (1 + sum(range(len(expected)))) + 1e-8 if quantized else 1e-6
            if abs(score - expectation) > slack:
                raise ResponseContractError("incompatible_score_expectation")
            if abs(score - expectation) > 1e-6:
                warnings.append(f"{key}:independent_score_quantization")
    usage = raw.get("usage")
    if not isinstance(usage, dict) or any(
        type(usage.get(k)) is not int or usage[k] < 0 for k in ("input_tokens", "output_tokens")
    ):
        raise ResponseContractError("invalid_usage")
    return {
        "model_resolved": raw["model"],
        "answers": answers,
        "usage": {k: usage[k] for k in ("input_tokens", "output_tokens")},
        "warnings": warnings,
    }


class JevClient:
    def __init__(self, api_key, *, config=None, transport=None, sleep=time.sleep):
        self.api_key = api_key
        self.config = config or JevConfig()
        self.sleep = sleep
        self.client = httpx.Client(
            timeout=self.config.timeout_seconds,
            transport=transport,
            follow_redirects=False,
            trust_env=False,
        )

    def close(self):
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def evaluate(self, state, questions, *, capture: Callable):
        validate_questions(questions)
        payload = {"model": self.config.model, "state": state, "questions": questions}
        encoded = canonical_json(payload).encode("utf-8")
        started = time.monotonic()
        receipts = []
        result = None
        if len(encoded) > self.config.max_request_bytes:
            error = "request_byte_budget_exceeded"
        elif not self.api_key:
            error = "credentials_missing"
        else:
            error = "transport_unavailable"
            for attempt in range(1, self.config.max_attempts + 1):
                retry = False
                delay = min(self.config.max_retry_seconds, 2 ** (attempt - 1))
                body = b""
                status = None
                try:
                    with self.client.stream(
                        "POST",
                        ENDPOINT,
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json",
                        },
                        content=encoded,
                    ) as response:
                        status = response.status_code
                        oversized = False
                        for chunk in response.iter_bytes():
                            if len(body) + len(chunk) > MAX_RESPONSE_BYTES:
                                body += chunk[: MAX_RESPONSE_BYTES - len(body)]
                                oversized = True
                                break
                            body += chunk
                        # Persist BEFORE parsing, schema checks, or HTTP classification.
                        receipts.append(capture(attempt, status, body, oversized))
                        if oversized:
                            error = "response_byte_budget_exceeded"
                            break
                        if status != 200:
                            error = f"http_{status}"
                            retry = status in {429, 500, 502, 503, 504, 529}
                            header = response.headers.get("retry-after")
                            if header:
                                try:
                                    delay = float(header)
                                except ValueError:
                                    try:
                                        delay = (
                                            parsedate_to_datetime(header) - now()
                                        ).total_seconds()
                                    except (ValueError, TypeError, OverflowError):
                                        pass
                                delay = max(0, min(self.config.max_retry_seconds, delay))
                        else:
                            try:
                                result = validate_response(
                                    strict_loads(body), questions, self.config.model
                                )
                            except ResponseContractError as exc:
                                error = str(exc)
                            break  # No retries for malformed semantic payloads.
                except httpx.HTTPError:
                    error = "transport_unavailable"
                    retry = True
                    receipts.append(capture(attempt, None, b"", False))
                if not retry or attempt == self.config.max_attempts:
                    break
                self.sleep(delay)
        return {
            "status": "available" if result else "unavailable",
            "error_code": None if result else error,
            "answers": result["answers"] if result else {},
            "model_resolved": result["model_resolved"] if result else None,
            "warnings": result["warnings"] if result else [],
            "usage": result["usage"] if result else {},
            "latency_ms": (time.monotonic() - started) * 1000,
            "receipt_ids": receipts,
        }


def authorize_bindings(ledger, bindings):
    seen = set()
    pending = []
    for ref in bindings:
        row = current(ledger, ref["kind"], ref["id"])
        if row["revision"] != ref["revision"]:
            raise PolicyError("Decision input revision changed")
        pending.append((ref["kind"], ref["id"]))
    while pending:
        kind, rid = pending.pop()
        if (kind, rid) in seen:
            continue
        seen.add((kind, rid))
        row = current(ledger, kind, rid)
        if kind == "rights":
            require_right(RightsGrant.model_validate(row["payload"]), "send_to_provider")
        pending.extend((d["kind"], d["id"]) for d in row["dependencies"])
    return seen


def run_decision(ledger, request, client, *, actor="local-operator"):
    bindings = request["bindings"]
    if not bindings:
        raise ValueError("A decision needs source bindings")
    authorize_bindings(ledger, bindings)
    validate_questions(request["questions"])
    key = digest(
        {
            **request,
            "endpoint": ENDPOINT,
            "model": client.config.model,
            "validator": VALIDATOR_VERSION,
        }
    )
    accounting = getattr(client, "operation_policy", None)
    journal = None
    if accounting is not None:
        if client.config.max_attempts != 1:
            raise ValueError("Accounted calls require one transport attempt per reservation")
        from statement_ledger.infrastructure.operations import OperationJournal

        journal = OperationJournal(ledger.store)
    retry_authorized = journal is not None and journal.retry_authorized(key, "typesafe")
    if not retry_authorized:
        cached = find_cached_decision(ledger, key, client.config)
        if cached is not None:
            return {"record": cached, "cache_hit": True}
        if journal is not None:
            recovered = journal.recover_decision(key, "typesafe")
            if recovered is not None and cache_eligible(recovered, client.config):
                authorize_bindings(ledger, recovered["bindings"])
                return {
                    "record": ledger.put("decision_run", recovered, actor=actor),
                    "cache_hit": True,
                }

    def capture(attempt, status, body, truncated):
        metadata = {
            **request,
            "endpoint": ENDPOINT,
            "model": client.config.model,
            "validator": VALIDATOR_VERSION,
        }
        if journal is not None:
            return journal.capture_receipt(
                operation, key, attempt, status, body, truncated, metadata
            )
        # Unaccounted direct calls have no operation; their receipts cannot be recovered
        # into another operation merely because the semantic request happens to match.
        return ledger.store.capture_provider_response(
            key, attempt, status, body, truncated, metadata
        )

    operation = "jev-" + uuid.uuid4().hex
    if journal is not None:
        journal.begin(
            operation,
            key,
            "typesafe",
            estimate_micro_usd=accounting[0],
            budget_micro_usd=accounting[1],
        )
    try:
        result = client.evaluate(request["state"], request["questions"], capture=capture)
        if journal is not None:
            if result["status"] == "available":
                journal.complete(
                    operation, {"usage": result["usage"], "receipt_ids": result["receipt_ids"]}
                )
            else:
                journal.unknown(operation)
    except BaseException:
        if journal is not None:
            journal.unknown(operation)
        raise
    record = {
        "id": "decision-" + uuid.uuid4().hex,
        "purpose": request["purpose"],
        "request_hash": key,
        "model_requested": client.config.model,
        "question_version": request["question_version"],
        "questions": request["questions"],
        "state_sha256": digest(request["state"]),
        "bindings": bindings,
        "input_ids": request.get("input_ids", []),
        "captured_at": now().isoformat(),
        **result,
    }
    return {"record": ledger.put("decision_run", record, actor=actor), "cache_hit": False}
