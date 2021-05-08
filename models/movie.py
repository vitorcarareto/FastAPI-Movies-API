from decimal import Decimal
from datetime import datetime
from typing import List
from pydantic import BaseModel, Field

# class MovieImages(BaseModel):
#     movie_id
#     image_url or image_base64


class Movie(BaseModel):
    id: int = None
    title: str
    description: str
    images: List[str]
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
