import uvicorn
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED
from routes.v1 import app as app_v1
from utils.db_object import db
from utils.security import authenticate_user, create_jwt_token


app = FastAPI(
    title="Movies API",
    description="API to manage movie rental.",
    version="1.0.0",
)

app.include_router(app_v1, prefix="/v1")


@app.get("/", tags=["Health check"])
async def health_check():
    return "OK"


@app.post('/login', tags=['Authentication'])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    jwt_user_dict = {"username": form_data.username, "password": form_data.password}
    user = await authenticate_user(**jwt_user_dict)
    if not user:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

    jwt_token = create_jwt_token(user)

    return {"access_token": jwt_token}


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
    uvicorn.run('run:app', host="0.0.0.0", port=8000, reload=False)
