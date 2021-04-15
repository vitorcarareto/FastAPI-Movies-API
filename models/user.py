from enum import Enum
from fastapi import Query
from pydantic import BaseModel


class Role(Enum):
    admin: str = "admin"
    personal: str = "personal"


class User(BaseModel):
    id: int = None
    username: str
    password: str
    email: str = None  #Query(..., regex=r"^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$")
    role: Role = Role.personal
