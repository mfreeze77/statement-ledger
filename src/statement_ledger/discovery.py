"""Compatibility import; implementation lives in pillars.discovery.planner."""

import importlib as _importlib
import sys as _sys

_sys.modules[__name__] = _importlib.import_module("statement_ledger.pillars.discovery.planner")
