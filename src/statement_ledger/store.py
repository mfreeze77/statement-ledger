"""Compatibility import; implementation is owned by infrastructure.sqlite_store."""

import sys
from importlib import import_module

sys.modules[__name__] = import_module("statement_ledger.infrastructure.sqlite_store")
