from datetime import datetime

from rescue_api.entities.base_entity import BaseRescueModel


class Dataset(BaseRescueModel):
    dg_id: str
    dg_organization_id: str
    dg_name: str
    dg_title: str
    dg_notes: str
    dg_metadata_created: datetime
    dg_metadata_modified: datetime
    access_direct_dl_count: int
    access_total_count: int
    dg_created: datetime
    organization_id: int
