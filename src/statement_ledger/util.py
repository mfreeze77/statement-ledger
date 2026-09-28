"""Compatibility import; implementation is owned by core.util."""

import sys
from importlib import import_module

sys.modules[__name__] = import_module("statement_ledger.core.util")
