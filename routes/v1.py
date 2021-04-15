from fastapi import Body, File, APIRouter
from models.user import User

app = APIRouter()


@app.get('/')
async def healthcheck():
    return {"message": f"{__name__}"}

@app.post('/user')
async def post_user(user: User):
    return {"message": user}


@app.get('/user/{user_id}')
async def get_user(user_id: int):
    return {"message": user_id}
