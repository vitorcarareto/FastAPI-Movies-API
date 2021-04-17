from utils.db import execute, fetch
from models.user import User

async def db_get_user(username):
    query = """
        select * from users
        where username = :username
    """
    values = {"username": username}
    result = await fetch(query, True, values)
    user_exists = bool(result)
    return User(**result) if user_exists else False

async def db_check_user(username):
    query = """
        select * from users
        where username = :username
    """
    values = {"username": username}
    result = await fetch(query, True, values)
    return bool(result)
