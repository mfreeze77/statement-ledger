import os

import pytest

from statement_ledger.demo import seed
from statement_ledger.service import Ledger
from statement_ledger.store import Store


@pytest.fixture
def ledger(tmp_path):
    store = Store(tmp_path / "ledger.sqlite3", initialize=True)
    try:
        yield Ledger(store)
    finally:
        store.close()


@pytest.fixture
def seeded(ledger):
    seed(ledger)
    return ledger


def pytest_collection_modifyitems(config, items):
    # Live tests need local secrets or hardware; CI and the cloud agent never run them.
    if os.getenv("SL_RUN_LIVE") == "1":
        return
    skip = pytest.mark.skip(reason="live test; set SL_RUN_LIVE=1 locally")
    for item in items:
        # Match the marker itself; item.keywords also holds parametrize ids and node names.
        if item.get_closest_marker("live"):
            item.add_marker(skip)
