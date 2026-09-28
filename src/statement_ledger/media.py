"""Compatibility import; implementation is owned by pillars.media.clipping."""

import sys
from importlib import import_module

sys.modules[__name__] = import_module("statement_ledger.pillars.media.clipping")
