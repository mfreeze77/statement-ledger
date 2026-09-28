"""Compatibility import; implementation is owned by contracts.models."""

import sys
from importlib import import_module

sys.modules[__name__] = import_module("statement_ledger.contracts.models")
