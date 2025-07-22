from fastapi import FastAPI
from routers import dispatch

app = FastAPI()

app.include_router(dispatch.router)

print(f"You can now connect on http://127.0.0.1:8000/")