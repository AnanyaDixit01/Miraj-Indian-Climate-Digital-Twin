"""Decode IMD 0.25-degree daily rainfall binary files into NetCDF."""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr


GRID_SHAPE = (129, 135)
LATITUDES = np.linspace(6.5, 38.5, GRID_SHAPE[0])
LONGITUDES = np.linspace(66.5, 100.0, GRID_SHAPE[1])
MISSING_VALUES = (99.9, -99.9)


def decode_grd(path) -> xr.DataArray:
    """Decode one IMD daily rainfall .grd file into a lat/lon DataArray.

    Parameters
    ----------
    path : str or pathlib.Path
        Path to a binary file containing 129 * 135 float32 values.

    Returns
    -------
    xarray.DataArray
        Rainfall grid with dimensions lat and lon. Missing-value flags
        99.9 and -99.9 are represented as NaN.

    Raises
    ------
    ValueError
        If the file does not contain exactly 129 * 135 float32 values.
    """
    path = Path(path)
    values = np.fromfile(path, dtype=np.float32)

    expected_size = GRID_SHAPE[0] * GRID_SHAPE[1]
    if values.size != expected_size:
        raise ValueError(
            f"{path} contains {values.size} values; expected "
            f"{expected_size} for grid shape {GRID_SHAPE}."
        )

    grid = values.reshape(GRID_SHAPE).astype(np.float32, copy=True)

    missing_mask = np.zeros(grid.shape, dtype=bool)
    for missing_value in MISSING_VALUES:
        missing_mask |= np.isclose(
            grid, missing_value, atol=1e-4, rtol=0
        )
    grid[missing_mask] = np.nan

    return xr.DataArray(
        grid,
        dims=("lat", "lon"),
        coords={
            "lat": (
                "lat",
                LATITUDES,
                {
                    "standard_name": "latitude",
                    "long_name": "latitude",
                    "units": "degrees_north",
                    "axis": "Y",
                },
            ),
            "lon": (
                "lon",
                LONGITUDES,
                {
                    "standard_name": "longitude",
                    "long_name": "longitude",
                    "units": "degrees_east",
                    "axis": "X",
                },
            ),
        },
        name="rainfall",
        attrs={
            "units": "mm",
            "long_name": "Daily Rainfall",
        },
    )


def stack_daily_files(input_path) -> xr.Dataset:
    """Decode and combine daily GRD files into a time-indexed dataset.

    Parameters
    ----------
    input_path : str or pathlib.Path
        A single .grd file or a directory containing daily .grd files.
        Filenames are sorted lexicographically.

    Returns
    -------
    xarray.Dataset
        Dataset with rainfall(time, lat, lon).
    """
    input_path = Path(input_path)

    if input_path.is_file():
        files = [input_path]
    elif input_path.is_dir():
        files = sorted(input_path.glob("*.grd"))
    else:
        raise FileNotFoundError(f"Input path does not exist: {input_path}")

    if not files:
        raise FileNotFoundError(f"No .grd files found in {input_path}")

    daily_arrays = [decode_grd(file) for file in files]

    # Use dates from filenames when they contain YYYYMMDD or YYYY-MM-DD.
    dates = []
    for file in files:
        date_text = file.stem.replace("-", "")
        parsed_date = pd.NaT

        for index in range(max(0, len(date_text) - 7)):
            candidate = date_text[index:index + 8]
            try:
                parsed_date = pd.to_datetime(candidate, format="%Y%m%d")
                break
            except ValueError:
                continue

        dates.append(parsed_date)

    # If filenames don't contain usable dates, use a sequential time index.
    if any(pd.isna(date) for date in dates):
        raise ValueError(
            "Could not extract a valid YYYYMMDD date from every filename. "
            "Please use filenames containing dates, such as rainfall_20240701.grd."
        )

    times = pd.DatetimeIndex(dates)

    combined = xr.concat(daily_arrays, dim=pd.Index(times, name="time"))
    combined.name = "rainfall"

    combined["time"].attrs.update(
        {
            "standard_name": "time",
            "axis": "T",
        }
    )

    combined.attrs.update(
        {
            "units": "mm",
            "long_name": "Daily Rainfall",
        }
    )

    dataset = combined.to_dataset()
    dataset.attrs.update(
        {
            "Conventions": "CF-1.8",
            "title": "IMD 0.25-degree Gridded Daily Rainfall",
            "source": "India Meteorological Department (IMD)",
        }
    )

    return dataset


def main():
    """Parse CLI arguments and save the decoded dataset as NetCDF4."""
    parser = argparse.ArgumentParser(
        description="Decode IMD daily rainfall GRD files into NetCDF4."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to one .grd file or a directory of .grd files.",
    )
    parser.add_argument(
        "--output",
        default="data/processed/IMD_Gridded_Rainfall_0.25_Real_v4.nc",
        help="Output NetCDF file path.",
    )
    args = parser.parse_args()

    dataset = stack_daily_files(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    dataset.to_netcdf(output_path, engine="netcdf4", format="NETCDF4")
    print(f"Decoded {dataset.sizes['time']} daily file(s) to {output_path}")


if __name__ == "__main__":
    main()
