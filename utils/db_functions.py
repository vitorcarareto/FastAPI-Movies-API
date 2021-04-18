from asyncpg.exceptions import UniqueViolationError
from utils.db import execute, fetch
from utils.db_object import db
from models.user import User
from models.movie import Movie, MovieLog


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


async def db_get_movies(sort: str, order: str, limit: int, offset: int, title: str = None, availability: bool = None):

    filter = ""
    values = {}
    if availability is True:
        filter += " and availability = true "
    elif availability is False:
        filter += " and availability = false "

    if title:
        values['title'] = title.replace(' ', '%')
        filter += " and title ilike '%'|| :title ||'%' "

    query = f"""
        select * from movies
        where true
          {filter}
        order by {sort} {order}, id
        limit {limit} offset {offset}
    """
    result = await fetch(query, False, values=values)
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


@db.transaction()
async def db_update_movie(movie: Movie, field_name: str, new_value):
    values = {"value": new_value, "movie_id": movie.id}
    query = f"""
        update movies
        set {field_name} = :value
        where id = :movie_id
        returning id
    """

    try:
        old_value = getattr(movie, field_name)
        if str(old_value) != str(new_value):
            log_values = {
                "movie_id": movie.id,
                "updated_field": field_name,
                "old_value": old_value,
                "new_value": str(new_value)
            }
            log_query = f"""
                insert into movies_log (movie_id, updated_field, old_value, new_value)
                values (:movie_id, :updated_field, :old_value, :new_value)
            """
            await execute(query, False, values)  # Update movie
            await execute(log_query, False, log_values)  # Log updated field and values
            setattr(movie, field_name, new_value)

        return movie
    except Exception as e:
        print(f"Error updating movie {movie.id}: {e}")


async def db_delete_movie(movie_id: int):
    values = {"movie_id": movie_id}
    query = """
        delete from movies
        where id = :movie_id
        returning id
    """

    try:
        movie_id = await execute(query, False, values)
        return movie_id
    except Exception as e:
        print(f"Error deleting movie {movie_id}: {e}")
