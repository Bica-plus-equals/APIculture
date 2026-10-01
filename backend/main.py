"""FastAPI entry point connecting the dashboard to the Python model layer."""

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title='APIculture API',
    version='0.1.0'
)

#frontend to backend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],)

@app.get('/')
def root():
    return {'message': 'Welcome to the APIculture API!'}

@app.get('/health')
def health():
    return {'status': 'ok'}

@app.get('/dates')
def get_dates():
    #These need to come from the database
    return {
        'dates': [
            '2021-04-01',
            '2021-04-15',
            '2021-05-01',
            '2021-05-15'
        ]
    }

@app.get('/image/{date}')
def get_image(date: str):
    #This needs to come from the database
    return {
        'date' :date,
        'status':'avalabke',
        'message': 'Image endpoint working'
    }

DATA_FOLDER = Path(__file__).parent.parent / "data/GEE Data"

@app.get('/api/raster')
def get_raster(date: str):

    filename = DATA_FOLDER / f'NDVI_{date}.tif'

    return FileResponse(filename)