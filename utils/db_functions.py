from asyncpg.exceptions import UniqueViolationError
from utils.db import execute, fetch
from models.user import User


async def db_get_user(username: str):
    query = """
        select * from users
        where username = :username
    """
    values = {"username": username}
    result = await fetch(query, True, values)
    user_exists = bool(result)
    return User(**result) if user_exists else False


async def db_get_user_by_id(user_id: int):
    query = """
        select * from users
        where id = :user_id
    """
    values = {"user_id": user_id}
    result = await fetch(query, True, values)
    user_exists = bool(result)
    return User(**result) if user_exists else False


async def db_check_user(username: str):
    query = """
        select * from users
        where username = :username
    """
    values = {"username": username}
    result = await fetch(query, True, values)
    return bool(result)


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

