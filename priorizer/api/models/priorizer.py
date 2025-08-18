from pydantic import BaseModel, Field, HttpUrl, field_validator
from typing import List, Any
import re

# TODO put in common with dispatcher
# Define a Pydantic model for asset to rescue
class AssetModel(BaseModel):
    path: str = Field(..., description="Asset path")
    name: str = Field(..., description="Asset name")
    priority: int = Field(..., description="Asset priority according to ranker")
    size_mb: float = Field(..., description="Asset estimated size")
    ds_id: str = Field(..., description="Dataset id")
    res_id: str = Field(..., description="Resource id")
    asset_id: str = Field(..., description="Asset id")
    url: Any = Field(..., description="Asset rescue url (Torrent magnet or organization link)")

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

# Define a Pydantic model for response serve by priorizer to dispatcher
class PriorizerResponse(BaseModel):
    asset: List[AssetModel] = Field(..., description="Ranked dataset list")