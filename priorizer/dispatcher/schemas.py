from pydantic import BaseModel
from typing import List, Optional

class AssetResponse(BaseModel):
    id: str  # Changé de asset_id à id
    url: str  # Changé de download_url à url
    size_mb: float
    priority: int
    name: str  # Ajouté si nécessaire

class DispatchRequest(BaseModel):
    free_space_gb: float
    node_id: Optional[str] = None

class ReleaseRequest(BaseModel):
    asset_id: str
    node_id: str

class CkanUpdate(BaseModel):
    asset_id: str
    new_priority: int  # Doit être entre 1 et 10

class CkanUpdateRequest(BaseModel):
    updates: List[CkanUpdate]