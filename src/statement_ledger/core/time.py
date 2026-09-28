from decimal import ROUND_HALF_UP, Decimal


def seconds_ms(value) -> int:
    d = Decimal(str(value))
    if not d.is_finite() or d < 0:
        raise ValueError("Invalid timestamp")
    return int((d * 1000).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
