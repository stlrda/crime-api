# API for Serving Crime Data
# All READ-ONLY Functions
# Use `uvicorn main:app` to run

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Need to Import Asynchronous Postgres Module...
# Need to Configure OpenAPI/Swagger Spec...

# Load Database Configuration


# Allow All CORS
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=['*'])

## Legacy Endpoints ##
# Necessary Until the Deprecation of Current Dashboard
@app.get('/legacy/coords')
async def legacy_coords():
    return None

@app.get('/legacy/latest')
async def legacy_latest():
    return None

@app.get('/legacy/crime')
async def legacy_crime():
    return None

@app.get('/legacy/nbhood')
async def legacy_nbhood():
    return None

@app.get('/legacy/district')
async def legacy_district():
    return None

@app.get('/legacy/catsum')
async def legacy_catsum():
    return None

@app.get('/legacy/range')
async def legacy_range():
    return None

@app.get('/legacy/trends')
async def legacy_trends():
    return None

## Version 2.0 Endpoints ##

# Render Documentation/Overview on Root
@app.get('/')
async def root():
    return {'message' : 'Welcome to the MapSTL API'}


# Get All Available Datasets
@app.get('/datasets')
async def datasets():
    return {'datasets' : 'object'}

# Get Dataset Time Information

# Get Geometric Points

# Get Polygons or Aggregations

# Save a Specific Map to a Permalink
@app.post('/save')
async def permalink():
    # Get the body with layers.json
    # Calculate a hash for this (MD5? Fast)
    # Store in a Database field
    # Return the hash value to the client
