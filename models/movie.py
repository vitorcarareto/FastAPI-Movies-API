from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field


class Movie(BaseModel):
    id: int = None
    title: str
    description: str
    stock: int = Field(None, gt=0)
    rental_price: Decimal
    sale_price: Decimal
    availability: bool  # Only admin can modify this field


class MovieLog(BaseModel):
    id: int = None
    movie_id: int
    updated_field: str
    old_value: str
    new_value: str
    updated_datetime: datetime
