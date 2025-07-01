from fastapi import FastAPI
from rescue_api.routers import v1
from rescue_api.settings import get_settings

settings = get_settings()

app = FastAPI(title=settings.app_name, version=settings.version)

# Add router
app.include_router(v1.router)
