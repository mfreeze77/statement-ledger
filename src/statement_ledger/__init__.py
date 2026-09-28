"""Standalone Statement Ledger."""

__version__ = "0.3.0"
from .acceleration_models import EXTENSION_KINDS
from .models import KINDS

KINDS.update(EXTENSION_KINDS)
