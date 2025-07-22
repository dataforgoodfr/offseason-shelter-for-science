from pydantic import BaseModel, Field, HttpUrl
from typing import Dict, List

# Define a Pydantic model for the request payload
class DispatchRequest(BaseModel):
    name: str = Field(..., description="Rescuer name")
    description: str = Field(..., description="Rescuer description")
    value: int = Field(..., description="Rescuer available space")

# Define a Pydantic model for asset to rescue
class AssetModel(BaseModel):
    path: str = Field(..., description="Dataset path")
    ds_id: str = Field(..., description="Dataset id")
    res_id: str = Field(..., description="Result id")

# Define a Pydantic model for the response payload
class DispatchResponse(BaseModel):
    status: str = Field(..., description="Response status")
    message: str = Field(..., description="Respons message")
    received_data: dict = Field(..., description="Requested payload")
    mock_data: dict[HttpUrl, List[AssetModel]] = Field(..., description="Dataset list")

