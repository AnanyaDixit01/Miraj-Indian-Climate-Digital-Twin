# Indian Climate Digital Twin - GIS Analytics Dashboard

## Data Sources and Licenses
- **India States Boundary**: The state boundary GeoJSON data (`data/india_states.geojson`) is sourced from the open-source repository [adarshbiradar/maps-geojson](https://github.com/adarshbiradar/maps-geojson).

---

## Setup Instructions

### 1. Clean Environment Setup
Create and activate a virtual environment:

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# On Linux / macOS:
source .venv/bin/activate
```

### 2. Install Dependencies
Install all required runtime and testing dependencies using `requirements.txt`:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

If installing dependencies individually or adding test/HTTP clients:
```bash
pip install pytest httpx
```

> [!NOTE]
> **NetCDF Engine Requirements (`netcdf4` / `scipy`):**
> `xarray` relies on backend engines to decode and parse NetCDF datasets:
> - **`netCDF4`**: Required for NetCDF-4 and HDF5-based files (`engine="netcdf4"`).
> - **`scipy`**: Fallback/default engine for classic NetCDF-3 32-bit/64-bit offset format files (`engine="scipy"`).
>
> Both `netcdf4` and `scipy` are included in `requirements.txt`. Ensure at least one compatible engine is installed to prevent backend parsing errors (`ValueError` or `OSError`) when calling `xr.open_dataset()`.

---

## Running the Application

### 1. Generate / Decode Sample Data
Ensure the sample NetCDF dataset is available:
```bash
python scripts/generate_mock_imd.py
```
*(or run `scripts/decoder.py` if decoding raw IMD binary/gridded data).*

### 2. Run the FastAPI Backend
Start the status and analytics API service:
```bash
uvicorn app.api:app --reload --host 0.0.0.0 --port 8000
```
Status endpoint: `GET http://localhost:8000/api/status`

### 3. Run the Streamlit Dashboard
Launch the interactive GIS dashboard:
```bash
streamlit run app/streamlit_app.py
```

The dashboard includes:
- State/UT, date, and climate-variable filters
- A boundary-masked state climate heatmap with hover values
- State mean, peak, coverage, and previous-day change indicators
- A national state/UT leaderboard and grid-level threshold filter
- CSV downloads for the national summary, selected grid cells, and state time series
- Temporal trend and value-distribution charts

### 4. Run Test Suites
Execute the spatial analysis, API, and Streamlit test suites:
```bash
python -m pytest -v tests/
```
