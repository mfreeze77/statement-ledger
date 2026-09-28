"""Compatibility import; implementation is owned by application.acceleration."""

import sys
from importlib import import_module

sys.modules[__name__] = import_module("statement_ledger.application.acceleration")
