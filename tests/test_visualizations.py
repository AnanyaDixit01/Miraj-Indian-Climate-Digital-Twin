"""Tests for dashboard visualization helpers."""

import numpy as np
import pytest
import xarray as xr

from src.visualizations import build_state_heatmap


def test_build_state_heatmap_contains_grid_and_boundary():
    """The state map should contain a heatmap and an outline trace."""
    data = xr.DataArray(
        [[1.0, np.nan], [2.0, 3.0]],
        dims=("lat", "lon"),
        coords={"lat": [10.0, 11.0], "lon": [75.0, 76.0]},
        name="rainfall",
    )

    figure = build_state_heatmap(
        data,
        ([75.0, 76.0, 76.0, 75.0], [10.0, 10.0, 11.0, 10.0]),
        "Example State",
        "Rainfall (mm)",
        "mm",
        "Blues",
    )

    assert len(figure.data) == 2
    assert figure.data[0].type == "heatmap"
    assert figure.data[1].type == "scatter"
    assert "Example State" in figure.layout.title.text


def test_build_state_heatmap_rejects_non_spatial_data():
    """A clear error should be raised for data without lat/lon dimensions."""
    data = xr.DataArray([1.0, 2.0], dims=("time",))

    with pytest.raises(ValueError, match="lat and lon"):
        build_state_heatmap(data, ([], []), "State", "Rainfall", "mm", "Blues")
