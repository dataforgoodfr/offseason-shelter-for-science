from fastapi import HTTPException, APIRouter
from fastapi.responses import JSONResponse
from models.priorizer import PriorizerResponse
import json
from os.path import join, dirname
from models.state import app_state

router = APIRouter()

@router.get('/')
async def root():
    data = f"Hello dispatcher 👋"
    return JSONResponse(content=data)

@router.post('/mock_ranking', response_model=PriorizerResponse)
async def mock_ranking():
    app_state._logger.info("________In mock priorizer")
    # Load mock data from the JSON file
    with open(join(dirname(__file__), '..', 'mock', 'mock_data.json')) as f:
        mock_ranking = json.load(f)

    priorizer_response = PriorizerResponse(
        asset=mock_ranking
    )
    print(f"mock_dispatch response: {priorizer_response}")

    return priorizer_response

@router.post('/ranking', response_model=PriorizerResponse)
async def ranking():
    app_state._logger.info("________In priorizer")
    # Call last priorizer ranking available
    result = app_state._priorizer.get_rank()
    app_state._logger.info(result)

    priorizer_response = PriorizerResponse(
        asset=result["assets"]
    )
    print(f"Priorizer response: {priorizer_response}")

    return priorizer_response
