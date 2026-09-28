"""Compatibility import; implementation is owned by core.policy."""

import sys
from importlib import import_module

sys.modules[__name__] = import_module("statement_ledger.core.policy")
