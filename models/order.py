from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel

class OrderType(Enum):
    purchase: str = "purchase"
    rental: str = "rental"

class Order(BaseModel):
    id: int = None
    movie_id: int = None
    user_id: int = None
    amount: int
    price_paid: Decimal = None
    order_type: OrderType
    order_datetime: datetime = None
    expected_return_date: date = None
    returned_date: date = None
    delay_penalty_paid: Decimal = None
