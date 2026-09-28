from statement_ledger.core.policy import PolicyError


def binding(row):
    return {"kind": row["kind"], "id": row["id"], "revision": row["revision"]}


def current(ledger, kind, rid):
    row = ledger.store.get(kind, rid)
    if not ledger.dependencies_current(kind, rid):
        raise PolicyError(f"Stale or expired source: {kind}:{rid}")
    return row
