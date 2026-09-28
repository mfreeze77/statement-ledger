"""Standalone Statement Ledger."""
__version__ = "0.2.0"
from .models import KINDS
from .acceleration_models import EXTENSION_KINDS
KINDS.update(EXTENSION_KINDS)
