from fastapi import APIRouter

router = APIRouter(prefix="/hello", tags=["test"])


@router.get("/")
async def root():
    return {"message": "Hello D4G"}
