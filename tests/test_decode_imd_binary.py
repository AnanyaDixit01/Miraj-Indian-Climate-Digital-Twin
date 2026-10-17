"""Tests for the IMD binary rainfall decoder."""

import numpy as np

from scripts.decode_imd_binary import decode_grd


def test_decode_grd_handles_missing_values(tmp_path):
    """Verify grid dimensions, coordinates, and missing-value conversion."""
    grid = np.full((129, 135), 12.5, dtype=np.float32)
    grid[0, 0] = 99.9
    grid[0, 1] = -99.9

    file_path = tmp_path / "rainfall_20240701.grd"
    grid.tofile(file_path)

    result = decode_grd(file_path)

    assert result.shape == (129, 135)
    assert result.dims == ("lat", "lon")
    assert result.lat.values[0] == 6.5
    assert np.isclose(result.lat.values[-1], 38.5)
    assert result.lon.values[0] == 66.5
    assert np.isclose(result.lon.values[-1], 100.0)

    assert np.isnan(result.values[0, 0])
    assert np.isnan(result.values[0, 1])
    assert result.values[0, 2] == 12.5
    assert not np.any(np.isclose(result.values, 99.9, equal_nan=False))
    assert not np.any(np.isclose(result.values, -99.9, equal_nan=False))