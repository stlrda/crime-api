# Models for Table and Queries

import sqlalchemy
from typing import List, Optional
from pydantic import BaseModel

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

# Define Crime ORM Models
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
