# Models for Table and Queries

import sqlalchemy
import datetime as dt
from typing import List, Optional
from pydantic import BaseModel, validator

# Define Crime Table
metadata = sqlalchemy.MetaData()

crime = sqlalchemy.Table(
    "crime",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer),
    sqlalchemy.Column("date", sqlalchemy.Date),
    sqlalchemy.Column("time", sqlalchemy.Time),
    sqlalchemy.Column("flag_crime", sqlalchemy.Boolean),
    sqlalchemy.Column("flag_unfounded", sqlalchemy.Boolean),
    sqlalchemy.Column("flag_admin", sqlalchemy.Boolean),
    sqlalchemy.Column("count", sqlalchemy.Boolean),
    sqlalchemy.Column("code", sqlalchemy.Float),
    sqlalchemy.Column("category", sqlalchemy.Text),
    sqlalchemy.Column("district", sqlalchemy.Integer),
    sqlalchemy.Column("description", sqlalchemy.Text),
    sqlalchemy.Column("neighborhood", sqlalchemy.Integer),
    sqlalchemy.Column("lon", sqlalchemy.Float),
    sqlalchemy.Column("lat", sqlalchemy.Float)
)

# Function to Truncate Coordinate Precision
def trunc_coord(coord: float) -> float:
    return round(coord, 5)

# Define Crime ORM Models
class LegacyCrimeLatest(BaseModel):
    crime_last_update: dt.date

class LegacyCrimeNeighborhood(BaseModel):
    neighborhood: str
    ucr_category: str
    Incidents: Optional[int]

class LegacyCrimeDistrict(BaseModel):
    district: str
    ucr_category: str
    Incidents: Optional[int]

class LegacyCrimeRange(BaseModel):
    db_id: int
    ucr_category: str
    wgs_x: Optional[float]
    wgs_y: Optional[float]

class CrimeLatest(BaseModel):
    latest: dt.date

class CrimePoints(BaseModel):
    id: int
    lon: Optional[float]
    lat: Optional[float]
    _trunc_lon = validator('lon', allow_reuse=True)(trunc_coord)
    _trunc_lat = validator('lat', allow_reuse=True)(trunc_coord)

class CrimeDetailed(BaseModel):
    id: int
    date: dt.date
    time: dt.time
    description: Optional[str]
    lon: Optional[float]
    lat: Optional[float]
    _trunc_lon = validator('lon', allow_reuse=True)(trunc_coord)
    _trunc_lat = validator('lat', allow_reuse=True)(trunc_coord)

class CrimeAggregate(BaseModel):
    region: int
    count: int