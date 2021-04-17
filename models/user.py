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

    def serialize(self, safe=True):
        """ Serialize the object in a dictionary. """
        d = self.dict()
        if safe:  # Drop sensitive data
            d.pop('password')
            d.pop('role')

        if d.get('role'):
            d['role'] = self.role.value

        return d
