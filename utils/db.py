from utils.db_object import db


async def execute(query, is_many, values=None):
    if is_many:
        returned_value = await db.execute_many(query=query, values=values)
    else:
        returned_value = await db.execute(query=query, values=values)

    return returned_value


async def fetch(query, is_one, values):
    if is_one:
        result = await db.fetch_one(query=query, values=values)
        output = dict(result) if result else None
    else:
        result = await db.fetch_all(query=query, values=values)
        output = [dict(row) for row in result] if result else None
    return output
