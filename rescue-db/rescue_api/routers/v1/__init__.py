from fastapi import APIRouter
from rescue_api.routers.v1 import hello_d4g

router = APIRouter(prefix="/v1")
router.include_router(hello_d4g.router)
