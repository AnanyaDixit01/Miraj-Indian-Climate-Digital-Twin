import pytest
import numpy as np
import xarray as xr
import geopandas as gpd
from shapely.geometry import Polygon
from unittest.mock import patch
from src.spatial_predictions import mask_region_boundary_local, get_all_states, get_outline_coords


@pytest.fixture
def mock_spatial_grid():
    """
    Creates a regular 2D coordinate grid with known values.
    Grid coordinates:
        lons: 0.0, 0.5, 1.0, 1.5, 2.0
        lats: 0.0, 0.5, 1.0, 1.5, 2.0
    Values: all set to 42.0 for clear distinction from NaN.
    """
    lons = np.array([0.0, 0.5, 1.0, 1.5, 2.0])
    lats = np.array([0.0, 0.5, 1.0, 1.5, 2.0])
    data = np.full((5, 5), 42.0)

    da = xr.DataArray(
        data,
        coords=[lats, lons],
        dims=["lat", "lon"],
        name="rainfall",
    )
    return da


@pytest.fixture
def mock_region_gdf():
    """
    Creates a mock GeoDataFrame with a rectangular polygon covering:
    lon: [0.5, 1.5], lat: [0.5, 1.5]
    """
    poly = Polygon([(0.5, 0.5), (1.5, 0.5), (1.5, 1.5), (0.5, 1.5), (0.5, 0.5)])
    return gpd.GeoDataFrame({"st_nm": ["MockRegion"], "geometry": [poly]})


def test_points_inside_boundary(mock_spatial_grid, mock_region_gdf):
    """
    Condition 1: Points inside the boundary.
    Verifies that grid cells located strictly inside the polygon geometry
    retain their original data values and are NOT masked to NaN.
    """
    with patch("src.spatial_predictions.gpd.read_file", return_value=mock_region_gdf):
        masked_data, bounds, centroid, outline = mask_region_boundary_local(
            mock_spatial_grid, "MockRegion"
        )

        # (1.0, 1.0) is strictly inside the box [0.5, 1.5] x [0.5, 1.5]
        inside_val = masked_data.sel(lat=1.0, lon=1.0).values
        assert not np.isnan(inside_val), "Interior point (1.0, 1.0) should not be NaN"
        assert inside_val == 42.0, f"Expected original value 42.0, got {inside_val}"


def test_points_outside_boundary(mock_spatial_grid, mock_region_gdf):
    """
    Condition 2: Points outside the boundary.
    Verifies that grid cells located strictly outside the polygon boundary
    are masked out and explicitly set to NaN.
    """
    with patch("src.spatial_predictions.gpd.read_file", return_value=mock_region_gdf):
        masked_data, bounds, centroid, outline = mask_region_boundary_local(
            mock_spatial_grid, "MockRegion"
        )

        # Exterior points across different quadrants outside [0.5, 1.5] x [0.5, 1.5]
        outside_coords = [
            (0.0, 0.0),  # Bottom-left exterior
            (0.0, 2.0),  # Top-left exterior
            (2.0, 0.0),  # Bottom-right exterior
            (2.0, 2.0),  # Top-right exterior
            (0.0, 1.0),  # West exterior
            (2.0, 1.0),  # East exterior
        ]

        for lat, lon in outside_coords:
            val = masked_data.sel(lat=lat, lon=lon).values
            assert np.isnan(val), f"Exterior point ({lat}, {lon}) should be masked to NaN"


def test_points_on_boundary(mock_spatial_grid, mock_region_gdf):
    """
    Condition 3: Points directly on the boundary.
    Verifies that points situated on the boundary edge or vertex are evaluated
    consistently by the containment path algorithm without crashing or corrupting data.
    """
    with patch("src.spatial_predictions.gpd.read_file", return_value=mock_region_gdf):
        masked_data, bounds, centroid, outline = mask_region_boundary_local(
            mock_spatial_grid, "MockRegion"
        )

        # Boundary points on the perimeter: lon/lat in {0.5, 1.5}
        boundary_coords = [
            (0.5, 0.5),  # Corner vertex
            (1.5, 1.5),  # Corner vertex
            (0.5, 1.0),  # Bottom edge
            (1.5, 1.0),  # Top edge
            (1.0, 0.5),  # Left edge
            (1.0, 1.5),  # Right edge
        ]

        # Verify all boundary points are valid float values (either preserved value or NaN per ray-cast rule)
        for lat, lon in boundary_coords:
            val = float(masked_data.sel(lat=lat, lon=lon).values)
            assert np.isnan(val) or val == 42.0, (
                f"Boundary point ({lat}, {lon}) must either be preserved (42.0) or NaN, got {val}"
            )

        # Specific deterministic checks for matplotlib Path ray-casting behavior:
        # matplotlib Path.contains_points includes bottom & right edges (lon=1.0, lat=0.5 and lat=1.0, lon=1.5)
        edge_included = masked_data.sel(lat=1.0, lon=0.5).values
        assert not np.isnan(edge_included), "Boundary edge point (1.0, 0.5) should be contained"
        assert edge_included == 42.0


def test_mask_region_metadata(mock_spatial_grid, mock_region_gdf):
    """
    Verifies that spatial metadata (bounds, centroid, outline coordinates)
    are correctly computed alongside the masked array.
    """
    with patch("src.spatial_predictions.gpd.read_file", return_value=mock_region_gdf):
        masked_data, bounds, centroid, outline = mask_region_boundary_local(
            mock_spatial_grid, "MockRegion"
        )

        # Expected bounds: (minx, maxx, miny, maxy) -> (0.5, 1.5, 0.5, 1.5)
        assert bounds == (0.5, 1.5, 0.5, 1.5)

        # Expected centroid: (1.0, 1.0)
        assert pytest.approx(centroid[0], 0.001) == 1.0
        assert pytest.approx(centroid[1], 0.001) == 1.0

        # Outline coords should contain lon and lat lists
        lon_lines, lat_lines = outline
        assert len(lon_lines) > 0
        assert len(lat_lines) > 0
        assert len(lon_lines) == len(lat_lines)

