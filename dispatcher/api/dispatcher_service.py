from fastapi import FastAPI
from routers import dispatch

app = FastAPI()

app.include_router(dispatch.router)