"""Auditable window recall, calibration diagnostics and operator-priced cost models."""

from __future__ import annotations

import math

from statement_ledger.contracts.acceleration import CalibrationRow
from statement_ledger.core.intervals import duration, intersection, merge, pairs


def _finite_nonnegative(value, name):
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or value < 0
    ):
        raise ValueError(f"{name} must be finite and nonnegative")
    return value


def evaluate_windows(
    selected, truth, duration_ms, *, event_id, training_event_ids=(), truth_complete=False
):
    if event_id in set(training_event_ids):
        raise ValueError("Evaluation event overlaps profile training events")
    sel = merge(selected, duration_ms=duration_ms)
    gold = merge(truth, duration_ms=duration_ms)
    turns = sorted(set(pairs(truth)))
    captured = duration(intersection(sel, gold))
    total = duration(gold)
    return {
        "event_id": event_id,
        "truth_complete": truth_complete,
        "selected_audio_ms": duration(sel),
        "target_audio_ms": total,
        "captured_target_audio_ms": captured,
        "missed_target_audio_ms": total - captured,
        "target_time_recall": captured / total if total else None,
        "fully_covered_turns": sum(
            duration(intersection(sel, [(a, b)])) == b - a for a, b in turns
        ),
        "gold_turns": len(turns),
        "audio_fraction": duration(sel) / duration_ms if duration_ms else None,
        "deployment_gate_passed": False,
        "limitation": "Metrics describe supplied labels; no proof of their completeness. No threshold is auto-promoted.",
    }


def calibration_report(rows, *, training_event_ids=(), bins=10):
    if not 2 <= bins <= 50:
        raise ValueError("bins must be 2..50")
    parsed = [CalibrationRow.model_validate(r) for r in rows]
    if not parsed:
        raise ValueError("Calibration evaluation needs labels")
    if set(training_event_ids) & {r.event_id for r in parsed}:
        raise ValueError("Training/evaluation event leakage")
    buckets = [[] for _ in range(bins)]
    for r in parsed:
        buckets[min(int(r.signal * bins), bins - 1)].append(r)
    out = []
    ece = 0
    for i, bucket in enumerate(buckets):
        mean = sum(r.signal for r in bucket) / len(bucket) if bucket else None
        actual = sum(r.target_present for r in bucket) / len(bucket) if bucket else None
        if bucket:
            ece += len(bucket) / len(parsed) * abs(mean - actual)
        out.append(
            {
                "lower": i / bins,
                "upper": (i + 1) / bins,
                "n": len(bucket),
                "mean_signal": mean,
                "observed_frequency": actual,
            }
        )
    return {
        "n": len(parsed),
        "events": len({r.event_id for r in parsed}),
        "bins": out,
        "brier_score": sum((r.signal - int(r.target_present)) ** 2 for r in parsed) / len(parsed),
        "expected_calibration_error": ece,
        "calibrator_fitted": False,
        "threshold_promoted": False,
        "limitation": "Diagnostic only. Window labels can be correlated within episodes; split and assess by event.",
    }


def estimate_cost(
    *,
    duration_ms,
    selected_audio_ms,
    audio_cost_per_minute,
    screening_input_tokens=0,
    price_per_million_input_tokens=0,
    verification_cost=0,
    overhead_cost=0,
    screening_output_tokens=0,
    price_per_million_output_tokens=0,
):
    for name, value in list(locals().items()):
        _finite_nonnegative(value, name)
    if selected_audio_ms > duration_ms:
        raise ValueError("Selected audio exceeds original duration")
    baseline = duration_ms / 60000 * audio_cost_per_minute
    screening = (
        screening_input_tokens / 1_000_000 * price_per_million_input_tokens
        + screening_output_tokens / 1_000_000 * price_per_million_output_tokens
    )
    optimized = (
        selected_audio_ms / 60000 * audio_cost_per_minute
        + screening
        + verification_cost
        + overhead_cost
    )
    return {
        "baseline_cost": baseline,
        "screening_cost": screening,
        "proposed_cost": optimized,
        "estimated_savings": baseline - optimized,
        "estimated_savings_fraction": (baseline - optimized) / baseline if baseline else None,
        "lower_estimated_cost_route": "selected_audio" if optimized < baseline else "full_audio",
        "measured": False,
        "currency": "operator_supplied_consistent_currency",
        "limitation": "User-supplied prices and volumes; excludes anything not included in those inputs.",
    }
