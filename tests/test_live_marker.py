"""The live marker gate: CI and the cloud agent must never execute live tests."""

import os

import pytest


@pytest.mark.live
def test_live_tests_run_only_when_opted_in():
    assert os.getenv("SL_RUN_LIVE") == "1"


@pytest.mark.parametrize("mode", ["live", "offline"])
def test_parametrize_id_named_live_is_not_skipped(mode):
    # Only @pytest.mark.live gates a test; an ordinary case named "live" must still run.
    assert mode in {"live", "offline"}
