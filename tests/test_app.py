import os
import pytest
from unittest.mock import patch
import streamlit as st
from streamlit.testing.v1 import AppTest

APP_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app", "streamlit_app.py"))


def test_app_launch_and_interact():
    """Verify standard app launch and dynamic selectbox interactions."""
    st.cache_resource.clear()
    at = AppTest.from_file(APP_PATH).run(timeout=30)
    assert not at.exception

    # Selectbox 0 is the State selector
    state_selectbox = at.sidebar.selectbox[0]
    if len(state_selectbox.options) > 1:
        new_state = state_selectbox.options[1]
        state_selectbox.select(new_state).run(timeout=30)

    assert not at.exception


def test_app_missing_dataset_fails_safely():
    """Verify app handles missing NetCDF dataset gracefully with st.error and st.stop."""
    st.cache_resource.clear()
    orig_exists = os.path.exists

    def mock_exists(path):
        if "sample_rainfall" in str(path):
            return False
        return orig_exists(path)

    with patch("os.path.exists", side_effect=mock_exists):
        at = AppTest.from_file(APP_PATH).run(timeout=30)
        # Should stop cleanly with zero unhandled exceptions
        assert not at.exception
        # Error message should instruct user to run the decoder script
        errors = [err.value for err in at.error]
        assert any("scripts/decoder.py" in str(msg) for msg in errors)


def test_app_corrupt_dataset_fails_safely():
    """Verify app handles NetCDF backend/corruption errors gracefully with st.error and st.stop."""
    st.cache_resource.clear()
    with patch("xarray.open_dataset", side_effect=OSError("NetCDF: Unknown file format")):
        at = AppTest.from_file(APP_PATH).run(timeout=30)
        # Should stop cleanly with zero unhandled exceptions
        assert not at.exception
        # Error message should indicate backend engine or file corruption
        errors = [err.value for err in at.error]
        assert any("Unable to parse NetCDF dataset" in str(msg) for msg in errors)
