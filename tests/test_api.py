import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.api import app

client = TestClient(app)


def test_api_status_online():
    """Test standard healthy status response when NetCDF dataset is available."""
    response = client.get("/api/status")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "online"
    assert "latest_timestamp" in data


def test_api_status_file_not_found():
    """Test 503 response and decoder guidance when dataset file is missing."""
    with patch("os.path.exists", return_value=False):
        response = client.get("/api/status")
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "offline"
        assert "scripts/decoder.py" in data["error"]


def test_api_status_netcdf_value_error():
    """Test 500 response when NetCDF engine fails due to ValueError."""
    with patch("os.path.exists", return_value=True), \
         patch("xarray.open_dataset", side_effect=ValueError("Engine 'netcdf4' not available")):
        response = client.get("/api/status")
        assert response.status_code == 500
        data = response.json()
        assert data["status"] == "error"
        assert "NetCDF backend engine error" in data["error"]


def test_api_status_netcdf_os_error():
    """Test 500 response when NetCDF parsing encounters an OSError (file corrupt)."""
    with patch("os.path.exists", return_value=True), \
         patch("xarray.open_dataset", side_effect=OSError("NetCDF: Unknown file format")):
        response = client.get("/api/status")
        assert response.status_code == 500
        data = response.json()
        assert data["status"] == "error"
        assert "NetCDF backend engine error" in data["error"]


def test_api_status_generic_exception():
    """Test 500 response when an unexpected Exception occurs."""
    with patch("os.path.exists", return_value=True), \
         patch("xarray.open_dataset", side_effect=RuntimeError("Unexpected memory crash")):
        response = client.get("/api/status")
        assert response.status_code == 500
        data = response.json()
        assert data["status"] == "error"
        assert "Internal server error" in data["error"]
