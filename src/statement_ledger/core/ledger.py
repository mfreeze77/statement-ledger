from __future__ import annotations

from typing import Any

from statement_ledger.contracts.models import KINDS, RightsGrant, now
from statement_ledger.core.policy import PolicyError
from statement_ledger.core.validation import ReadLedger, ValidatorRegistry


class Ledger:
    def __init__(self, store: Any, validators: ValidatorRegistry):
        validators.check(KINDS)
        self.store = store
        self.validators = validators

    def _validate(self, kind, payload, ref):
        self.validators.validate(kind, ReadLedger(self), payload, ref)

    def put(
        self,
        kind: str,
        data: dict[str, Any],
        expected_revision: int = 0,
        actor: str = "local-operator",
    ) -> dict:
        if kind not in KINDS:
            raise ValueError(f"Unknown record kind: {kind}")
        if not actor.strip():
            raise ValueError("Actor is required")
        if expected_revision < 0:
            raise ValueError("Expected revision cannot be negative")
        model = KINDS[kind].model_validate(data)
        payload = model.model_dump(mode="json")
        with self.store.transaction():
            dependencies: dict[tuple[str, str], dict] = {}

            def ref(k: str, rid: str) -> dict:
                record = self.store.get(k, rid)
                if record["stale"] or not self.dependencies_current(k, rid):
                    raise PolicyError(f"Stale dependency: {k}:{rid}; revalidate it first")
                if self.store.would_cycle((kind, model.id), (k, rid)):
                    raise PolicyError("Dependency would create a cycle")
                dependencies[k, rid] = {"kind": k, "id": rid, "revision": record["revision"]}
                return record["payload"]

            self._validate(kind, payload, ref)
            return self.store.write(
                kind,
                payload,
                sorted(dependencies.values(), key=lambda x: (x["kind"], x["id"])),
                expected_revision,
                actor,
            )

    def dependencies_current(self, kind: str, record_id: str) -> bool:
        todo, seen = ([(kind, record_id)], set())
        while todo:
            key = todo.pop()
            if key in seen:
                continue
            seen.add(key)
            row = self.store.get(*key)
            if row["stale"]:
                return False
            if key[0] == "rights":
                grant = RightsGrant.model_validate(row["payload"])
                if grant.expires_at and grant.expires_at <= now():
                    return False
            for d in row["dependencies"]:
                parent = self.store.get(d["kind"], d["id"])
                if parent["revision"] != d["revision"]:
                    return False
                todo.append((d["kind"], d["id"]))
        return True
