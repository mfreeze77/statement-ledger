"""Sealed validation registry and deliberately read-only validation views."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any, cast

Validator = Callable[[Any, dict[str, Any], Callable[[str, str], dict[str, Any]]], None]


class ReadStore:
    def __init__(self, store: Any) -> None:
        self.__store = store

    def get(self, kind: str, record_id: str, revision: int | None = None) -> dict[str, Any]:
        return cast(dict[str, Any], self.__store.get(kind, record_id, revision))

    def all(self, kind: str) -> list[dict[str, Any]]:
        return cast(list[dict[str, Any]], self.__store.all(kind))

    def provider_receipt(self, receipt_id: str) -> dict[str, Any]:
        return cast(dict[str, Any], self.__store.provider_receipt(receipt_id))


class ReadLedger:
    def __init__(self, ledger: Any) -> None:
        self.__ledger = ledger
        self.store = ReadStore(ledger.store)

    def dependencies_current(self, kind: str, record_id: str) -> bool:
        return bool(self.__ledger.dependencies_current(kind, record_id))


class ValidatorRegistry:
    def __init__(self) -> None:
        self._validators: dict[str, Validator] = {}
        self._sealed = False

    def register(self, kind: str, validator: Validator) -> None:
        if self._sealed or kind in self._validators:
            raise ValueError("Duplicate registration or sealed registry")
        self._validators[kind] = validator

    def check(self, kinds: Mapping[str, Any]) -> None:
        if set(self._validators) != set(kinds):
            raise ValueError("Exactly one validator is required for every writable record kind")
        self._sealed = True

    def validate(
        self,
        kind: str,
        ledger: ReadLedger,
        payload: dict[str, Any],
        ref: Callable[[str, str], dict[str, Any]],
    ) -> None:
        self._validators[kind](ledger, payload, ref)
