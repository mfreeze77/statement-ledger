class Conflict(ValueError):
    pass


class Missing(KeyError):
    pass


class TransientFailure(RuntimeError):
    """A bounded retry is safe for this non-paid operation."""
