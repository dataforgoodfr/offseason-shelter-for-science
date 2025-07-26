from fastapi import HTTPException, APIRouter
from fastapi.responses import JSONResponse
from models.payload import DispatchRequest, DispatchResponse
import json
from os.path import join, dirname

router = APIRouter()

@router.get('/')
async def root():
    data = f"Hello rescuer 👋"
    return JSONResponse(content=data)

@router.post('/mock_dispatch', response_model=DispatchResponse)
async def mock_dispatch(payload: DispatchRequest):
    # Load mock data from the JSON file
    print(f"mock_dispatch payload: {payload}")
    with open(join(dirname(__file__), '..', 'mock', 'mock_data.json')) as f:
        mock_dispatch = json.load(f)

    distpatch_response = DispatchResponse(
        status="success",
        message="Payload received and processed",
        received_data=payload.dict(),
        mock_data=mock_dispatch
    )
    print(f"mock_dispatch response: {distpatch_response}")

    return distpatch_response