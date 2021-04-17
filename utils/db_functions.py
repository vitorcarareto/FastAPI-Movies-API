from asyncpg.exceptions import UniqueViolationError
from utils.db import execute, fetch
from models.user import User
from models.movie import Movie


async def db_get_user(username: str):
    query = """
        select * from users
        where username = :username
    """
    values = {"username": username}
    result = await fetch(query, True, values)
    exists = bool(result)
    return User(**result) if exists else False


async def db_get_user_by_id(user_id: int):
    query = """
        select * from users
        where id = :user_id
    """
    values = {"user_id": user_id}
    result = await fetch(query, True, values)
    exists = bool(result)
    return User(**result) if exists else False


async def db_insert_user(user: User):
    query = """
        insert into users (username, password, email, role)
        values (:username, :password, :email, :role)
        on conflict do nothing
        returning id
    """
    values = user.dict()
    values.pop('id')
    try:
        user_id = await execute(query, False, values)
        db_user = await db_get_user_by_id(user_id)
        return db_user
    except UniqueViolationError as e:
        print(f"Already exists: {e}")


async def db_update_user(user_id: int, field_name: str, value):
    values = {"value": value, "user_id": user_id}
    query = f"""
        update users
        set {field_name} = :value
        where id = :user_id
        returning id
    """

    try:
        user_id = await execute(query, False, values)
        db_user = await db_get_user_by_id(user_id)
        return db_user
    except Exception as e:
        print(f"Error updating user {user_id}: {e}")


async def db_get_movie(movie_id: int):
    query = """
        select * from movies
        where id = :movie_id
    """
    values = {"movie_id": movie_id}
    result = await fetch(query, True, values)
    exists = bool(result)
    return Movie(**result) if exists else False


async def db_get_movies(sort: str, order: str, limit: int, offset: int, availability: bool = None):

    filter = ""
    if availability is True:
        filter += "and availability = true"
    elif availability is False:
        filter += "and availability = False"

    query = f"""
        select * from movies
        where true
          {filter}
        order by {sort} {order}, id
        limit {limit} offset {offset}
    """
    result = await fetch(query, False, values=None)
    exists = bool(result)
    return result if exists else False


async def db_insert_movie(movie: Movie):
    query = """
        insert into movies (title, description, stock, rental_price, sale_price, availability)
        values (:title, :description, :stock, :rental_price, :sale_price, :availability)
        on conflict do nothing
        returning id
    """
    values = movie.dict()
    values.pop('id', None)
    try:
        movie_id = await execute(query, False, values=values)
        db_movie = await db_get_movie(movie_id)
        return db_movie
    except UniqueViolationError as e:
        print(f"Already exists: {e}")
