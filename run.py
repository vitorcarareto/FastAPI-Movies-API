import uvicorn
from fastapi import FastAPI
from datetime import datetime
from starlette.requests import Request
from routes.v1 import app as app_v1
from utils.db_object import db

app = FastAPI()

app.mount('/v1', app_v1)


@app.get("/")
async def health_check():
    return {"OK"}


@app.on_event("startup")
async def connect_db():
    await db.connect()
    return db


@app.on_event("shutdown")
async def disconnect_db(db):
    await db.disconnect()


@app.middleware("http")
async def middleware(request: Request, call_next):
    start_time = datetime.utcnow()

    response = await call_next(request)

    # Modify response
    execution_time = (datetime.utcnow() - start_time).microseconds
    response.headers["x-execution-time"] = str(execution_time)
    return response


if __name__ == "__main__":
    uvicorn.run('run:app', host="0.0.0.0", port=8000, reload=True)
