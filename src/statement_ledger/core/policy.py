from statement_ledger.contracts.models import RightsGrant, Scope, now


class PolicyError(ValueError):
    pass


def require_right(grant: RightsGrant, operation: str, source_id: str | None = None) -> None:
    if source_id is not None and grant.source_id != source_id:
        raise PolicyError("Rights grant belongs to another source")
    if grant.expires_at and grant.expires_at <= now():
        raise PolicyError("Rights grant has expired")
    if operation not in grant.allowed:
        raise PolicyError(f"Operation is not permitted by rights grant: {operation}")


def scope_match(left: Scope, right: Scope) -> dict:
    """Conservative candidate compatibility; never a verdict or automatic claim merge."""
    required = ("entity", "metric", "geography", "period", "unit", "definition")
    missing = [key for key in required if not getattr(left, key) or not getattr(right, key)]
    differences = [key for key in Scope.model_fields if getattr(left, key) != getattr(right, key)]
    return {
        "compatible_candidate": not missing and not differences,
        "missing": missing,
        "differences": differences,
        "automatic_review_reuse": False,
    }
