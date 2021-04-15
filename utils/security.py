from datetime import datetime, timedelta
import time
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from starlette.status import HTTP_401_UNAUTHORIZED
from utils.const import JWT_EXPIRATION_TIME_MINUTES, JWT_SECRET_KEY, JWT_ALGORITHM
from models.user import User


jwt_fake_user = User(**{"username": "vitorcarareto", "password": "$2b$12$eJO.75FBs98nmww2wz0cyu22aq3vGTeanm4wEeUKIRDq4YlbmmZNy", "email": "vitor.carareto@gmail.com"})  # TODO Remove


pwd_context = CryptContext(schemes=["bcrypt"])
oauth_schema = OAuth2PasswordBearer(tokenUrl='/login')


def get_hashed_password(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        print(f"Error verifying password: {e}")

    return False


def authenticate_user(user: User):
    """ Authenticate username and password to give JWT token """
    if user.username == jwt_fake_user.username:
        if verify_password(user.password, jwt_fake_user.password):
            return user

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


def check_jwt_token(jwt_token: str = Depends(oauth_schema)):
    """ Check whether JWT token is correct """
    try:
        jwt_payload = jwt.decode(jwt_token, JWT_SECRET_KEY, algorithms=JWT_ALGORITHM)
        username = jwt_payload.get("sub")
        expiration = jwt_payload.get("exp")
        if time.time() < expiration:
            if jwt_fake_user.username == username:
                return final_checks(username)

    except Exception as e:
        print(f"Error checking JWT: {e}")
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)


def final_checks(username: str):
    """ Last checking and returning final result """
    # Perform any extra checks here
    return True
