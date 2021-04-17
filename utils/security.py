from datetime import datetime, timedelta
import time
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN
from models.user import User, Role
from utils.db_functions import db_get_user
from utils.const import (
    JWT_EXPIRATION_TIME_MINUTES,
    JWT_ALGORITHM,
    JWT_SECRET_KEY,
    JWT_EXPIRED_MSG,
    JWT_INVALID_MSG,
)


pwd_context = CryptContext(schemes=["bcrypt"])
oauth_schema = OAuth2PasswordBearer(tokenUrl='/login')
optional_oauth_schema = OAuth2PasswordBearer(tokenUrl='/login', auto_error=False)


def get_hashed_password(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        print(f"Error verifying password: {e}")

    return False


async def authenticate_user(username, password):
    """ Authenticate username and password to give JWT token """
    db_user = await db_get_user(username)
    plain_password = password
    hashed_password = db_user.password

    if verify_password(plain_password, hashed_password):
        return db_user

    return None


def create_jwt_token(user: User):
    """ Create access JWT token """
    expiration = datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_TIME_MINUTES)
    jwt_payload = {
        "sub": user.username,
        "exp": expiration,
    }
    jwt_token = jwt.encode(jwt_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    return jwt_token


async def verify_jwt_user(jwt_token: str):
    """ Verify the user from the JWT token and return it.
        If user is not found, return None.
        If the JWT is invalid, raise an exception (expired or malformed).
    """
    if not jwt_token:
        return None
    try:
        jwt_payload = jwt.decode(jwt_token, JWT_SECRET_KEY, algorithms=JWT_ALGORITHM)
        username = jwt_payload.get("sub")
        expiration = jwt_payload.get("exp")
        if time.time() < expiration:
            user = await db_get_user(username)
            return user
        else:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED, detail=JWT_EXPIRED_MSG
            )
    except Exception as e:
        print(f"Error checking JWT: {e}")
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)


async def check_optional_jwt_token(jwt_token: str = Depends(optional_oauth_schema)):
    """ Check whether optional JWT token is correct. """
    user = await verify_jwt_user(jwt_token)
    return user


async def check_jwt_token(jwt_token: str = Depends(oauth_schema)):
    """ Check whether JWT token is correct """
    user = await verify_jwt_user(jwt_token)
    if not user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail=JWT_INVALID_MSG
        )
    return user


def validate_admin(user: User, raise_exceptions=True):
    """ Check if user has admin role """
    is_admin = False
    if user and user.role == Role.admin.value:
        is_admin = True
    else:
        if raise_exceptions:
            raise HTTPException(status_code=HTTP_403_FORBIDDEN)
    return is_admin
