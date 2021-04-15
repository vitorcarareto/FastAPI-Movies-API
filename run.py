import uvicorn
from fastapi import FastAPI
from routes.v1 import app as app_v1

app = FastAPI()

app.mount('/v1', app_v1)


@app.get('/')
async def healthcheck():
    return {"message": "Health check"}

if __name__ == "__main__":
    uvicorn.run('run:app', host="0.0.0.0", port=8000, reload=True)
