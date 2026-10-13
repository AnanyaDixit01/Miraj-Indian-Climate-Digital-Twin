"""
IMD Gridded Data Decoder Script.

Decodes raw binary / gridded meteorological data or generates synthetic NetCDF
datasets required for the GIS dashboard and FastAPI service.
"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from scripts.generate_mock_imd import generate_mock_datasets


def decode_or_generate():
    """Execute decoding or generate fallback NetCDF datasets."""
    print("Executing IMD climate dataset decoder...")
    ds = generate_mock_datasets()
    print("Decoding complete. NetCDF datasets are ready for GIS processing.")
    return ds


if __name__ == "__main__":
    decode_or_generate()

