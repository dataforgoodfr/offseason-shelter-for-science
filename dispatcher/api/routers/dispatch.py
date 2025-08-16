from models.state import app_state
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
async def mock_dispatch(request: DispatchRequest):
    app_state._logger.info("________In mock dispatch")
    # Load mock data from the JSON file
    print(f"mock_dispatch payload: {request}")
    with open(join(dirname(__file__), '..', 'mock', 'mock_data.json')) as f:
        mock_dispatch = json.load(f)

    distpatch_response = DispatchResponse(
        status="success",
        message="Request received and processed",
        received_data=request.dict(),
        asset=mock_dispatch
    )
    print(f"mock_dispatch response: {distpatch_response}")

    return distpatch_response

@router.post('/dispatch', response_model=DispatchResponse)
async def dispatch(request: DispatchRequest):
    app_state._logger.info("________In dispatch")
    # Call dispatcher logic
    result = app_state._dispatcher.allocate_assets(
        free_space_mb=request.free_space_gb * 1024,
        node_id=request.node_id
    )
    app_state._logger.info(result)
    if not result:
        raise HTTPException(
            status_code=404,
            detail="No available assets matching the criteria"
        )

    distpatch_response = DispatchResponse(
        status="success",
        message="Request received and processed",
        received_data=request.dict(),
        asset=result["assets"]
    )
    print(f"Dispatch response: {distpatch_response}")

    return distpatch_response
