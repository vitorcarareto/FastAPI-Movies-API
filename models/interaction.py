from datetime import datetime
from enum import Enum
from pydantic import BaseModel


class InteractionType(Enum):
    like: str = "like"


class Interaction(BaseModel):
    id: int = None
    user_id: int
    movie_id: int
    interaction_type: InteractionType
    interaction_datetime: datetime = None
