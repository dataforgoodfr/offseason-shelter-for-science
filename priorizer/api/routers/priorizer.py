from fastapi import HTTPException, APIRouter
from fastapi.responses import JSONResponse
from models.priorizer import PriorizerResponse
import json
from os.path import join, dirname
from models.state import app_state
from typing import List

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
    
    app_state._logger.info(f"mock_dispatch response: {priorizer_response}")
    return priorizer_response

@router.post('/ranking', response_model=PriorizerResponse)
async def ranking():
    """ Request dataset_ranks latest rank"""
    app_state._logger.info("________In priorizer")
    # Call last priorizer ranking available
    result = app_state._priorizer.get_rank()
    
    app_state._logger.info(f"Rank size: {len(result['assets'])}")
    # TODO May need refactoring for network optimization purpose
    priorizer_response = PriorizerResponse(
        asset=result["assets"]
    )
    app_state._logger.info("Priorizer response ready")
    app_state._logger.info(f"Priorizer response: {priorizer_response}")

    return priorizer_response

@router.post('/test_ranking', response_model=List)
async def test_ranking():
    """ Compute new ranks """
    app_state._logger.info("________In priorizer rank")
    # Compute updated ranks
    ranks = app_state._priorizer.compute_rank()
 
    app_state._logger.info(f"Ranked assets: {len(ranks)}")
    app_state._logger.info("New ranking available")

    return ranks
