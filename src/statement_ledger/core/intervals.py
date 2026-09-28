"""Half-open integer millisecond interval algebra; never sums overlapping work twice."""

from __future__ import annotations

from statement_ledger.contracts.acceleration import Interval


def pairs(values):
    return [
        (v.start_ms, v.end_ms)
        if isinstance(v, Interval)
        else (v["start_ms"], v["end_ms"])
        if isinstance(v, dict)
        else tuple(v)
        for v in values
    ]


def merge(values, *, duration_ms=None):
    items = []
    for start, end in pairs(values):
        if type(start) is not int or type(end) is not int or start < 0 or end <= start:
            raise ValueError("Expected positive half-open integer millisecond intervals")
        if duration_ms is not None and end > duration_ms:
            raise ValueError("Interval exceeds asset duration")
        items.append((start, end))
    out = []
    for start, end in sorted(items):
        if out and start <= out[-1][1]:
            out[-1] = (out[-1][0], max(end, out[-1][1]))
        else:
            out.append((start, end))
    return out


def dictionaries(values):
    return [{"start_ms": a, "end_ms": b} for a, b in merge(values)]


def duration(values):
    return sum(b - a for a, b in merge(values))


def complement(values, duration_ms):
    if type(duration_ms) is not int or duration_ms < 0:
        raise ValueError("Invalid duration")
    cursor = 0
    out = []
    for start, end in merge(values, duration_ms=duration_ms):
        if start > cursor:
            out.append((cursor, start))
        cursor = end
    if cursor < duration_ms:
        out.append((cursor, duration_ms))
    return out


def intersection(left, right):
    a, b = merge(left), merge(right)
    i = j = 0
    out = []
    while i < len(a) and j < len(b):
        start, end = max(a[i][0], b[j][0]), min(a[i][1], b[j][1])
        if start < end:
            out.append((start, end))
        if a[i][1] < b[j][1]:
            i += 1
        else:
            j += 1
    return out


def pad(values, padding_ms, duration_ms):
    if type(padding_ms) is not int or padding_ms < 0:
        raise ValueError("Invalid padding")
    return merge(
        [
            (max(0, a - padding_ms), min(duration_ms, b + padding_ms))
            for a, b in merge(values, duration_ms=duration_ms)
        ],
        duration_ms=duration_ms,
    )
