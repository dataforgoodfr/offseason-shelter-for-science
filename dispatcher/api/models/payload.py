from pydantic import BaseModel, Field, HttpUrl, field_validator
import re
from typing import Dict, List, Optional, Any
from enum import Enum


class Status(Enum):
    success = "SUCCESS"
    fail = "FAIL"


# Define a Pydantic model for the request payload
class DispatchRequest(BaseModel):
    name: str = Field(..., description="Rescuer name")
    description: str = Field(..., description="Rescuer description")
    free_space_gb: float = Field(..., description="Rescuer available space")
    node_id: Optional[str] = Field(None, description="Node id")

# Define a Pydantic model for asset to rescue
class AssetModel(BaseModel):
    path: str = Field(..., description="Asset path")
    name: str = Field(..., description="Asset name")
    priority: int = Field(..., description="Asset priority according to ranker")
    size_mb: Optional[float] = Field(..., description="Asset estimated size")
    ds_id: str = Field(..., description="Dataset id")
    res_id: str = Field(..., description="Resource id")
    asset_id: str = Field(..., description="Asset id")
    url: Any = Field(..., description="Asset rescue url (Torrent magnet or organization link)")
    magnet_link: Any = Field(default=None, description="Torrent magnet link available after downloading the asset.")
    status: Status = Field(default=None, description="Status of the asset's rescue.")

    @field_validator('url')
    def validate_url(cls, v: Any) -> Any:
        if isinstance(v, str):
            try:
                HttpUrl(v)
            except:
                pattern = r'magnet:\?xt=urn:[a-z0-9]+:[a-zA-Z0-9]{1,40}'
                if not re.match(pattern, v):
                    raise ValueError("Invalid magnet link or URL format")
        return v

# Define a Pydantic model for the response payload
class DispatchResponse(BaseModel):
    status: str = Field(..., description="Response status")
    message: str = Field(..., description="Response message")
    received_data: dict = Field(..., description="Requested payload")
    asset: List[AssetModel] = Field(..., description="Dataset list")


class RescuesRequest(BaseModel):
    rescuer_id: int = Field(..., description="Rescuer id")
    message: str = Field(..., description="Message given by the application")
    assets: List[AssetModel] = Field(..., description="List of assets for which the rescue is over")


class RescuesResponse(DispatchResponse):
    asset: Optional[List[AssetModel]] = Field(default=None, description="Dataset list")
    updated_rescues: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="List of rescued assets that were updated in the database.",
    )
    inserted_rescues: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="List of rescued assets that were inserted in the database.",
    )
    not_committed_rescues: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="List of rescued assets for which an error happened when we tried to commit it to the database.",
    )
