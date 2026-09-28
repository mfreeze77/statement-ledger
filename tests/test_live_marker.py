"""The live marker gate: CI and the cloud agent must never execute live tests."""
import os
import pytest

@pytest.mark.live
def test_live_tests_run_only_when_opted_in():
    assert os.getenv("SL_RUN_LIVE")=="1"
