from fastapi import FastAPI, Body, Header, File, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette.status import HTTP_201_CREATED, HTTP_401_UNAUTHORIZED
from models.user import User
from utils.security import authenticate_user, create_jwt_token, check_jwt_token

app = FastAPI(root_path='/v1')

@app.get('/')
async def healthcheck():
    return {"message": f"{__name__}"}

@app.post('/user', status_code=HTTP_201_CREATED)
async def post_user(user: User):
    return {"message": user}

@app.get('/user/{user_id}')
async def get_user(user_id: int, jwt: bool=Depends(check_jwt_token)):
    return {"message": user_id}

@app.post('/login')
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    jwt_user_dict = {"username": form_data.username, "password": form_data.password}
    jwt_user = User(**jwt_user_dict)
    user = authenticate_user(jwt_user)
    if user is None:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

    jwt_token = create_jwt_token(user)

    return {"token": jwt_token}
