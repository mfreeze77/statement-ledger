"""Compatibility import; implementation is owned by infrastructure.providers.speech."""

import sys
from importlib import import_module

sys.modules[__name__] = import_module("statement_ledger.infrastructure.providers.speech")
