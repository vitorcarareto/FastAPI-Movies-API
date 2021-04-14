from fastapi import Body, File, APIRouter

app = APIRouter()


@app.get('/')
async def healthcheck():
    return {"message": f"{__name__}"}

