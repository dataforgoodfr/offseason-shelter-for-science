from models.state import app_state
from fastapi import HTTPException, APIRouter
from fastapi.responses import JSONResponse
from models.payload import DispatchRequest, DispatchResponse, Rescues
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

    dispatch_response = DispatchResponse(
        status="success",
        message="Request received and processed",
        received_data=request.dict(),
        asset=mock_dispatch
    )
    print(f"mock_dispatch response: {dispatch_response}")

    return dispatch_response

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
            status_code=422,
            detail="No available assets matching the criteria",
        )

    dispatch_response = DispatchResponse(
        status="success",
        message="Request received and processed",
        received_data=request.dict(),
        asset=result["assets"]
    )
    print(f"Dispatch response: {dispatch_response}")

    return dispatch_response

@router.put('/rescues', response_model=DispatchResponse)
async def update_rescues(rescues: Rescues):
    app_state._logger.info("________Update rescues after asset downloads")

    # Call dispatcher logic
    result = app_state._dispatcher.upsert_rescues(
        rescuer_id=rescues.rescuer_id,
        assets=rescues.assets,
    )
    app_state._logger.info(result)

    if result["action_status"] == "FAIL":
        return HTTPException(
            status_code=500,
            detail="An error happened when saving the data, the rescues couldn't be updated, please retry later.",
        )

    dispatch_response = DispatchResponse(
        status="success",
        message="Request received and processed",
        received_data=rescues.dict(),
        asset=rescues.assets,
    )
    print(f"Dispatch response: {dispatch_response}")

    return dispatch_response
