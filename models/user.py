from enum import Enum
from pydantic import BaseModel, EmailStr


class Role(Enum):
    admin: str = "admin"
    personal: str = "personal"


class User(BaseModel):
    id: int = None
    username: str
    email: EmailStr = None
    password: str
    role: Role = Role.personal

    class Config:
        use_enum_values = True
