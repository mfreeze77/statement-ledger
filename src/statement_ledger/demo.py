"""Compatibility import; implementation is owned by application.demo."""

import sys
from importlib import import_module

sys.modules[__name__] = import_module("statement_ledger.application.demo")
