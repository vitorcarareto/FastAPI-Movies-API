from fastapi import APIRouter, FastAPI, Body, Header, File, Depends, HTTPException
from starlette.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from typing import List
from models.user import User, Role
from models.movie import Movie
from utils.security import check_jwt_token, check_optional_jwt_token, get_hashed_password, validate_admin
from utils.db_functions import db_get_user_by_id, db_insert_user, db_update_user, db_insert_movie, db_get_movie, db_get_movies, db_update_movie, db_delete_movie

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

@app.patch('/users/{user_id}/role', response_model=User, tags=['Users'])
async def patch_user(user_id: int, value: str = Body(..., embed=True), user: User = Depends(check_jwt_token)):
    validate_admin(user)  # As an user with admin role I want to be able to change the role of any user.

    user = await db_get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)

    try:
        role = Role(value)
    except Exception as e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST)

    if user.role != role.value:  # No need to access the database if the value did not change.
        user = await db_update_user(user_id, field_name='role', value=value)

    return user


@app.post('/movies', status_code=HTTP_201_CREATED, response_model=Movie, tags=['Movies'])
async def post_movie(movie: Movie, user: User = Depends(check_jwt_token)):
    validate_admin(user)  # Only admins can add movies.
    try:
        movie = await db_insert_movie(movie)
    except Exception as e:
        print(f"Error inserting movie: {e}")
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST)
    return movie


@app.get('/movies', response_model=List[Movie], response_model_include=["id", "title", "stock", "rental_price", "sale_price", "availability"], tags=['Movies'])
async def get_movies(sort: str = "title", order: str = "asc", limit: int = 10, offset: int = 0, title: str = None, availability: bool = None, user: User = Depends(check_optional_jwt_token)):
    if not validate_admin(user, raise_exceptions=False):
        availability = True  # As an user I’m able to see only the available movies
    movies = await db_get_movies(sort, order, limit, offset, title, availability)
    if movies:
        return movies

    raise HTTPException(status_code=HTTP_404_NOT_FOUND)


@app.get('/movies/{movie_id}', response_model=Movie, tags=['Movies'])
async def get_movie(movie_id: int):
    movie = await db_get_movie(movie_id)
    if not movie:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)
    return movie


@app.patch('/movies/{movie_id}/{field_name}', response_model=Movie, tags=['Movies'])
async def patch_movie(movie_id: int, field_name: str, value: str = Body(..., embed=True), user: User = Depends(check_jwt_token)):
    validate_admin(user)  # Only admins can modify movies.

    movie = await db_get_movie(movie_id)
    if not movie:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)
    elif not hasattr(movie, field_name):  # Validation to avoid SQL injection
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST)

    movie = await db_update_movie(movie, field_name, value)
    return movie


@app.delete('/movies/{movie_id}', tags=['Movies'])
async def delete_movie(movie_id: int, user: User = Depends(check_jwt_token)):
    validate_admin(user)  # Only admins can modify movies.

    movie = await db_get_movie(movie_id)
    if not movie:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)
    await db_delete_movie(movie_id)
    return {"message": "Deleted successfully."}
