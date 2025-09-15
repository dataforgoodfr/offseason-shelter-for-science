import json
from os.path import join, dirname

from models.payload import DispatchRequest, DispatchResponse, RescuesRequest, RescuesResponse
from models.state import app_state
from fastapi import HTTPException, APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from rescue_api.database import get_db

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
    # Call dispatcher logic with priorizer integration
    result = await app_state._dispatcher.allocate_assets(
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

@router.post('/assets-downloaded', response_model=RescuesResponse)
async def upsert_rescues(request: RescuesRequest, db: Session = Depends(get_db)):
    app_state._logger.info("________Upsert rescues after downloading assets")

    if not request.assets:
        raise HTTPException(
            status_code=422,
            detail="The rescues don't contain any asset, "
                   "make sure they have at least one asset to be able to upsert them.",
        )

    # Call dispatcher logic
    result = app_state._dispatcher.upsert_rescues_to_db(
        rescuer_id=request.rescuer_id,
        assets=request.assets,
        db=db,
    )
    app_state._logger.info(result)

    if not result:
        raise HTTPException(
            status_code=422,
            detail="The error can be the following: the rescuer doesn't exist in the database; or at least one asset "
                   "doesn't exist in the database; or the asset data you provided don't match the ones in the "
                   "database. Make sure to provide an existing rescuer, existing assets and correct asset data.",
        )
    elif not result["updated_rescues"] and not result["inserted_rescues"]:
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Something went wrong when saving the data, the rescues below couldn't be upserted, "
                           "please retry later.",
                "not_committed_rescues": result["not_committed_rescues"],
            },
        )

    response = RescuesResponse(
        status="success",
        message="Request received and processed",
        received_data=request.dict(),
        asset=request.assets,
        updated_rescues=result["updated_rescues"],
        inserted_rescues=result["inserted_rescues"],
        not_committed_rescues=result["not_committed_rescues"],
    )
    print(f"Dispatch response: {response}")

    return response
