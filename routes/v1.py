from fastapi import FastAPI, Body, Header, File, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND
from models.user import User, Role
from utils.security import authenticate_user, create_jwt_token, check_jwt_token, get_hashed_password
from utils.db_functions import db_get_user_by_id, db_insert_user

app = FastAPI(root_path='/v1')


@app.get('/')
async def healthcheck():
    return {"message": f"{__name__}"}


@app.post('/user', status_code=HTTP_201_CREATED, response_model=User, response_model_include=["id", "username", "email", "role"])
async def post_user(user: User):
    user.password = get_hashed_password(user.password)
    user = await db_insert_user(user)
    return user


@app.get('/user/{user_id}', response_model=User, response_model_include=["id", "username", "email", "role"])
async def get_user(user_id: int, user: bool = Depends(check_jwt_token)):
    if user and user.id == user_id:
        return user

    raise HTTPException(status_code=HTTP_404_NOT_FOUND)


@app.post('/login')
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    jwt_user_dict = {"username": form_data.username, "password": form_data.password}
    user = await authenticate_user(**jwt_user_dict)
    if not user:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

    jwt_token = create_jwt_token(user)

    return {"token": jwt_token}
