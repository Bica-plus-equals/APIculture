"""FastAPI entry point connecting the dashboard to the Python model layer."""

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pathlib import Path

app = FastAPI()

DATA_FOLDER = Path(__file__).parent.parent / "data/GEE Data"

@app.get('/api/raster')
def get_raster(date: str):

    filename = DATA_FOLDER / f'NDVI_{date}.tif'

    return FileResponse(filename)