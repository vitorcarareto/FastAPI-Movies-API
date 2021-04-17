from fastapi import APIRouter, FastAPI, Body, Header, File, Depends, HTTPException
from starlette.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND
from typing import List
from models.user import User, Role
from models.movie import Movie
from utils.security import authenticate_user, create_jwt_token, check_jwt_token, check_optional_jwt_token, get_hashed_password
from utils.db_functions import db_get_user_by_id, db_insert_user, db_insert_movie, db_get_movie, db_get_movies

# app = FastAPI(openapi_prefix='/v1')
app = APIRouter()


@app.post('/users', status_code=HTTP_201_CREATED, response_model=User, response_model_include=["id", "username", "email", "role"], tags=['Users'])
async def post_user(user: User):
    user.password = get_hashed_password(user.password)
    user = await db_insert_user(user)
    if not user:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST)
    return user


@app.get('/users/{user_id}', response_model=User, response_model_include=["id", "username", "email", "role"], tags=['Users'])
async def get_user(user_id: int, user: User = Depends(check_jwt_token)):
    if user and user.id == user_id:
        return user

    raise HTTPException(status_code=HTTP_404_NOT_FOUND)


@app.post('/movies', status_code=HTTP_201_CREATED, response_model=Movie, tags=['Movies'])
async def post_movie(movie: Movie, user: User = Depends(check_jwt_token)):
    if user and user.role != Role.admin.value:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN)

    try:
        movie = await db_insert_movie(movie)
    except Exception as e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST)
    return movie


@app.get('/movies', response_model=List[Movie], response_model_include=["id", "title", "stock", "rental_price", "sale_price", "availability"], tags=['Movies'])
async def get_movies(sort: str = "title", order: str = "asc", limit: int = 10, offset: int = 0, availability: bool = None, user: User = Depends(check_optional_jwt_token)):
    if user and user.role != Role.admin.value:
        availability = True  # As an user I’m able to see only the available movies
    movies = await db_get_movies(sort, order, limit, offset, availability)
    if movies:
        return movies

    raise HTTPException(status_code=HTTP_404_NOT_FOUND)


@app.get('/movies/{movie_id}', response_model=Movie, tags=['Movies'])
async def get_movie(movie_id: int):
    movies = await db_get_movie(movie_id)
    if movies:
        return movies

    raise HTTPException(status_code=HTTP_404_NOT_FOUND)
