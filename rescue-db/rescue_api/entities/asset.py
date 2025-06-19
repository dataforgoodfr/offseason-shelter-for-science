from datetime import datetime

from rescue_api.entities.base_entity import BaseRescueModel


class AssetKind(BaseRescueModel):
    name: str


class Asset(BaseRescueModel):
    url: str
    kind_id: int
    resource_id: int
