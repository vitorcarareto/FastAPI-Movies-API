import asyncio
from databases import Database
from utils.const import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME

async def connect_db():
    db = Database(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    await db.connect()
    return db

async def disconnect_db(db):
    await db.disconnect()


async def execute(query, is_many, values=None):
    db = await connect_db()

    if is_many:
        await db.execute_many(query=query, values=values)
    else:
        await db.execute(query=query, values=values)

    await disconnect_db(db)

async def fetch(query, is_one, values):
    db = await connect_db()

    if is_one:
        result = await db.fetch_one(query=query, values=values)
        output = dict(result) if result else None
    else:
        result = await db.fetch_all(query=query, values=values)
        output = [dict(row) for row in result] if result else None

    await disconnect_db(db)
    return output
