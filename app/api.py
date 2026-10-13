import os
import logging
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
import xarray as xr

# Configure logger
logger = logging.getLogger(__name__)

app = FastAPI(
    title="GIS Climate API",
    description="Backend API for spatial climate analytics and dataset health monitoring.",
    version="1.0.0",
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "sample", "sample_rainfall_v3.nc")

@app.get("/api/status")
def get_status():
    """
    Check the health status of the API and NetCDF climate dataset.

    Returns:
        JSONResponse with HTTP 200 and dataset metadata when online.
        JSONResponse with HTTP 503 if the dataset file is missing.
        JSONResponse with HTTP 500 if the NetCDF engine fails or file is corrupt.
    """
    try:
        if not os.path.exists(DATA_PATH):
            raise FileNotFoundError(f"Dataset file not found at: {DATA_PATH}")

        with xr.open_dataset(DATA_PATH) as ds:
            latest_time = str(ds.time.values[-1])
            return {"status": "online", "latest_timestamp": latest_time}

    except FileNotFoundError as exc:
        logger.warning("Dataset file not found: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "offline",
                "error": "Dataset missing. Run scripts/decoder.py first.",
            },
        )

    except (ValueError, OSError) as exc:
        logger.error("NetCDF engine/backend parse error: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "error": f"NetCDF backend engine error: Unable to read dataset. Ensure netcdf4 or scipy is installed and dataset is not corrupted. Details: {str(exc)}",
            },
        )

    except Exception as exc:
        logger.exception("Unexpected error while checking status: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "error": f"Internal server error: {str(exc)}",
            },
        )
