"""Compatibility validation facade."""

from statement_ledger.application.ledger import validators
from statement_ledger.core.validation import ReadLedger


def validate_extension(ledger, kind, payload, ref):
    return validators().validate(kind, ReadLedger(ledger), payload, ref)
