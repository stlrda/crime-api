# API for St Louis Crime DB
#
import os
import databases
import sqlalchemy
import json
from datetime import datetime, timedelta, date
from fastapi import FastAPI, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from starlette.responses import RedirectResponse

from models import *

## Load Database Configuration
DB_HOST = os.environ['DB_HOST']
DB_PORT = os.environ['DB_PORT']
DB_NAME = os.environ['DB_NAME']
DB_USER = os.environ['DB_USER']
DB_PASS = os.environ['DB_PASS']
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
database = databases.Database(DATABASE_URL)

engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# Allow All CORS
app = FastAPI(title='STL Crime API')
app.add_middleware(CORSMiddleware, allow_origins=['*'])

## Connect to DB on Startup ##
@app.on_event('startup')
async def startup():
    await database.connect()
@app.on_event('shutdown')
async def shutdown():
    await database.disconnect()


## Legacy Endpoints ##
# Necessary Until the Deprecation of Current Dashboard
@app.get('/legacy/latest', response_model=LegacyCrimeLatest)
async def legacy_latest():
    query = "SELECT crime_last_update FROM update"
    return await database.fetch_one(query=query)

@app.get('/legacy/nbhood', response_model=List[LegacyCrimeNeighborhood])
async def legacy_nbhood(year: int, month: str, gun: Optional[str] = False):
    month = {
        'January': 1,
        'February': 2,
        'March': 3,
        'April': 4,
        'May': 5,
        'June': 6,
        'July': 7,
        'August': 8,
        'September': 9,
        'October': 10,
        'November': 11,
        'December': 12
    }[month]
    start = datetime(year, month, 1)
    if month == 12:
        year += 1
        month = 1
    else:
        month += 1
    end = datetime(year, month, 1)
    query = "SELECT neighborhood::INTEGER, category as ucr_category, SUM(CASE WHEN count THEN 1 END) as \"Incidents\" FROM crime WHERE date >= :start AND date < :end GROUP BY neighborhood, category;"
    values = {"start" : start, "end" : end}
    return await database.fetch_all(query=query, values=values)

@app.get('/legacy/district', response_model=List[LegacyCrimeDistrict])
async def legacy_district(year: int, month: str, gun: Optional[str] = False):
    month = {
        'January': 1,
        'February': 2,
        'March': 3,
        'April': 4,
        'May': 5,
        'June': 6,
        'July': 7,
        'August': 8,
        'September': 9,
        'October': 10,
        'November': 11,
        'December': 12
    }[month]
    start = datetime(year, month, 1)
    if month == 12:
        year += 1
        month = 1
    else:
        month += 1
    end = datetime(year, month, 1)
    query = "SELECT district::INTEGER, category as ucr_category, SUM(CASE WHEN count THEN 1 END) as \"Incidents\" FROM crime WHERE date >= :start AND date < :end GROUP BY district, category;"
    values = {"start" : start, "end" : end}
    return await database.fetch_all(query=query, values=values)

@app.get('/legacy/range', response_model=List[LegacyCrimeRange])
async def legacy_range(start: str, end: str, ucr: str, gun: Optional[str] = False):
    if end == 'NA':
        end = start
    start = datetime.strptime(start, '%Y-%m-%d')
    end = datetime.strptime(end, '%Y-%m-%d')
    # parse ucr as json
    categories = json.loads(ucr)
    # in query, need an in statment
    query = "SELECT id as db_id, category as ucr_category, lon as wgs_x, lat as wgs_y FROM crime WHERE date >= :start AND date <= :end AND category = ANY(:categories);"
    values = {"start": start, "end": end, "categories": categories}
    return await database.fetch_all(query=query, values=values)

@app.get('/legacy/trends')
async def legacy_trends(start: str, end: str, ucr: str, gun: Optional[str] = False):
    # Different schema from original, handled shiny server side instead of API
    start = datetime.strptime(start, '%Y-%m-%d').date()
    end = datetime.strptime(end, '%Y-%m-%d').date()
    # parse ucr as json
    categories = json.loads(ucr)
    if categories == {}:
        categories = []
    query = "SELECT date as date_occur, category, SUM(CASE WHEN count THEN 1 END) FROM crime WHERE date >= :start AND date <= :end AND category = ANY(:categories) GROUP BY date, category;" 
    values = {"start" : start, "end" : end, "categories": categories}
    return await database.fetch_all(query=query, values=values)

## Version 2.0 Endpoints ##

# Redirect Root to Docs
@app.get('/')
async def get_api_docs():
    response = RedirectResponse(url='/redoc')
    return response

# Get Latest Date
@app.get('/latest', response_model=CrimeLatest)
async def latest_data():
    query = "SELECT (date_trunc('month', crime_last_update::date) + interval '1 month' - interval '1 day')::date AS latest FROM update;"
    return await database.fetch_one(query=query)

# Get Point Level Coordinates
@app.get('/crime/', response_model=List[CrimePoints])
async def crime_points(start: date, end: date, category: str):
    query = "SELECT id, lon, lat FROM crime WHERE count = true AND date >= :start AND date <= :end AND LOWER(category) = LOWER(:category);"
    values = {'start': start, 'end': end, 'category': category}
    return await database.fetch_all(query=query, values=values)

@app.get('/crime/detailed', response_model=List[CrimeDetailed])
async def crime_detailed(start: date, end: date, category: str):
    query = "SELECT id, date, time, description, lon, lat FROM crime WHERE count = true AND date >= :start AND date <= :end AND LOWER(category) = LOWER(:category);"
    values = {'start': start, 'end': end, 'category': category}
    return await database.fetch_all(query=query, values=values)

# Get Geometric Aggregations
@app.get('/crime/{geometry}', response_model=List[CrimeAggregate])
async def crime_aggregate(start: date, end: date, geometry: str, category: str):
    geometry = geometry.lower()
    category = category.lower()
    if geometry == 'neighborhood':
        query = "SELECT neighborhood AS region, SUM(CASE WHEN count THEN 1 END) as count FROM crime WHERE date >= :start AND date <= :end AND LOWER(category) = :category GROUP BY neighborhood;"
    elif geometry == 'district':
        query = "SELECT district AS region, SUM(CASE WHEN count THEN 1 END) as count FROM crime WHERE date >= :start AND date <= :end AND LOWER(category) = :category GROUP BY district;"
    else:
        raise HTTPException(status_code=400, detail='Unsupported Geometry. Try one of "neighborhood" or "district"')
    values = {'start': start, 'end': end, 'category': category}
    # Need to find and implement geometries, geojson, type checking model and feature collection response
    # Can also consolidate query here
    return await database.fetch_all(query=query, values=values)

# Get Temporal Aggregations
# @app.get('crime/trends')
# async def crime_trends(start: str, end: str, interval: str, category: list, correct: bool, total: bool):
#     # Interval should be one of days, weeks, months, years
#     # Correct Specifies whether to apply seasonal correction
#     # Total Specifies whether to just get a total count (i.e. total of all categories in a single month)
#     # Need to Figure out Postgres for Time Series
#     return None

# Download Entire Research Files
# @app.get('crime/download')
# async def crime_download(start: date, end: date, category: Optional[str] = 'all'):
#     # Can we automatically export this as a CSV? Figure out pydantic models
#     return None

## Modify API Docs ##
def api_docs(openapi_prefix: str):
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title='St. Louis Crime',
        version='0.1.0',
        description='Automatically Updated, Clean Crime Data from the Saint Louis Metropolitan Police Department, provided by the St. Louis Regional Data Alliance in partnership with the Insititute for Public Health at Washington University.<br><br>If you\'d prefer to interact with queries in browser, see the <a href=\'/docs\'>Swagger UI</a>',
        routes=app.routes,#[13:], # Need to Verify this to Obfuscate Some Routes from Docs
        openapi_prefix=openapi_prefix
    )
    openapi_schema['info']['x-logo'] = {
        'url' : 'https://stldata.org/wp-content/uploads/2019/06/rda-favicon.png' # Need a more permanent source
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = api_docs
