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
