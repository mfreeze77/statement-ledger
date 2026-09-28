import os
import pytest
from statement_ledger.store import Store
from statement_ledger.service import Ledger
from statement_ledger.demo import seed

@pytest.fixture
def ledger(tmp_path):
    store=Store(tmp_path/"ledger.sqlite3")
    try:yield Ledger(store)
    finally:store.close()

@pytest.fixture
def seeded(ledger):
    seed(ledger)
    return ledger

def pytest_collection_modifyitems(config,items):
    # Live tests need local secrets or hardware; CI and the cloud agent never run them.
    if os.getenv("SL_RUN_LIVE")=="1":return
    skip=pytest.mark.skip(reason="live test; set SL_RUN_LIVE=1 locally")
    for item in items:
        if "live" in item.keywords:item.add_marker(skip)
