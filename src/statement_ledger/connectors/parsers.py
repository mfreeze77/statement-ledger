"""Compatibility import; implementation is owned by pillars.discovery.parsers."""

import sys
from importlib import import_module

sys.modules[__name__] = import_module("statement_ledger.pillars.discovery.parsers")
