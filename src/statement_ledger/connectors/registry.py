"""Compatibility import; implementation is owned by contracts.source_catalog."""

import sys
from importlib import import_module

sys.modules[__name__] = import_module("statement_ledger.contracts.source_catalog")
