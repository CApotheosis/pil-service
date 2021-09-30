"""PIL Services - Assessment application module."""
from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hi"}


handler = Mangum(app=app)
