from datetime import datetime

from rescue_api.entities.base_entity import BaseRescueModel


class Resource(BaseRescueModel):
    dg_id: str
    dg_name: str
    dg_description: str
    dg_resource_locator_function: str
    dg_resource_locator_protocol: str
    dg_mimetype: str
    dg_state: str
    dg_created: datetime
    dg_metadata_modified: datetime
    dg_url: str
    resource_type: str
    dataset_id: int
