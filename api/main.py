# API for Serving Crime Data
# All READ-ONLY Functions
# Use `uvicorn main:app` to run

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from starlette.responses import RedirectResponse

from fastapi.openapi.utils import get_openapi

# Need to Import Asynchronous Postgres Module...
# Need to Configure OpenAPI/Swagger Spec...

# Load Database Configuration


# Allow All CORS
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=['*'])

## Legacy Endpoints ##
# Necessary Until the Deprecation of Current Dashboard
@app.get('/legacy/coords')
async def legacy_coords(year: int, month: str, gun: bool, ucr: list):
    return None

@app.get('/legacy/latest')
async def legacy_latest():
    return None

@app.get('/legacy/crime')
async def legacy_crime(dbid: int):
    return None

@app.get('/legacy/nbhood')
async def legacy_nbhood(year: int, month: str, gun: bool):
    return None

@app.get('/legacy/district')
async def legacy_district(year: int, month: str, gun: bool):
    return None

@app.get('/legacy/catsum')
async def legacy_catsum(categories: list):
    return None

@app.get('/legacy/range')
async def legacy_range(start: str, end: str, gun: bool, ucr: list):
    return None

@app.get('/legacy/trends')
async def legacy_trends(start: str, end: str, gun: bool, ucr: list):
    return None

## Version 2.0 Endpoints ##

# Redirect Root to Docs
@app.get('/')
async def get_api_docs():
    response = RedirectResponse(url='/redoc')
    return response

# Get Latest Date
@app.get('/latest')
async def latest_data():
    print(list(app.routes))
    return 'Latest Date'

# Get Point Level Coordinates
@app.get('/crime')
async def crime_points(start: str, end: str, category: list, simple: bool):
    # Simple Designates should we return all field or just points
    return None

# Get Geometric Aggregations
@app.get('crime/{geometry}')
async def crime_aggregate(start: str, end: str, geometry: str, category: list):
    return None

# Get Temporal Aggregations
@app.get('crime/trends')
async def crime_trends(start: str, end: str, interval: str, category: list, correct: bool, total: bool):
    # Interval should be one of days, weeks, months, years
    # Correct Specifies whether to apply seasonal correction
    # Total Specifies whether to just get a total count (i.e. total of all categories in a single month)
    return None


## Modify API Docs ##
def api_docs(openapi_prefix: str):
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title='St. Louis Crime',
        version='0.1.0',
        description='Automatically Updated, Clean Crime Data from the Saint Louis Metropolitan Police Department, provided by the St. Louis Regional Data Alliance in partnership with the Insititute for Public Health at Washington University.<br><br>If you\'d prefer to interact with queries in browser, see the <a href=\'/docs\'>Swagger UI</a>',
        routes=app.routes[13:], # Need to Verify this to Obfuscate Some Routes from Docs
        openapi_prefix=openapi_prefix
    )
    openapi_schema['info']['x-logo'] = {
        'url' : 'https://stldata.org/wp-content/uploads/2019/06/rda-favicon.png' # Need a more permanent source
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = api_docs






##TODO Implement Map Saving via Permalinks in DB

# # Save a Specific Map to a Permalink
# @app.post('/save')
# async def permalink():
#     # Get the body with layers.json
#     # Calculate a hash for this (MD5? Fast)
#     # Store in a Database field
#     # Return the hash value to the client
#     return None