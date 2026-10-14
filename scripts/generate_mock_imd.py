import os
import numpy as np
import pandas as pd
import xarray as xr
from scipy.ndimage import gaussian_filter

# Standard IMD 0.25 degree coordinate ranges
lons = np.linspace(66.5, 100.0, 135)
lats = np.linspace(6.5, 38.5, 129)
times = pd.date_range("2024-07-01", "2024-07-07")
shape = (len(times), len(lats), len(lons))

np.random.seed(42)


def generate_field(base_val, scale, filter_sigma, min_val, max_val):
    """Generate spatially continuous synthetic climate variables using Gaussian smoothing."""
    noise = np.random.randn(*shape) * scale + base_val
    smoothed = gaussian_filter(noise, sigma=[0, filter_sigma, filter_sigma])
    smoothed = (smoothed - smoothed.min()) / (smoothed.max() - smoothed.min())
    smoothed = smoothed * (max_val - min_val) + min_val
    return np.clip(smoothed, min_val, max_val)


def generate_mock_datasets():
    """Build and write synthetic NetCDF climate datasets to data/sample directory."""
    rainfall = generate_field(0, 50, 4.0, 0, 80)
    temperature = generate_field(30, 15, 3.0, 20, 45)
    humidity = generate_field(60, 30, 3.5, 30, 95)
    wind_speed = generate_field(15, 20, 2.5, 5, 55)

    ds = xr.Dataset(
        {
            "rainfall": (["time", "lat", "lon"], rainfall, {"units": "mm", "long_name": "Daily Rainfall"}),
            "temperature": (["time", "lat", "lon"], temperature, {"units": "°C", "long_name": "Max Daily Temperature"}),
            "humidity": (["time", "lat", "lon"], humidity, {"units": "%", "long_name": "Relative Humidity"}),
            "wind_speed": (["time", "lat", "lon"], wind_speed, {"units": "km/h", "long_name": "Surface Wind Speed"}),
        },
        coords={"lon": lons, "lat": lats, "time": times},
    )

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_dir, "data", "sample")
    os.makedirs(output_dir, exist_ok=True)

    # Write primary and versioned datasets
    for filename in ["sample_rainfall.nc", "sample_rainfall_v2.nc", "sample_rainfall_v3.nc"]:
        target_path = os.path.join(output_dir, filename)
        ds.to_netcdf(target_path)
        print(f"Synthetic NetCDF created at {target_path}")

    return ds


if __name__ == "__main__":
    generate_mock_datasets()
