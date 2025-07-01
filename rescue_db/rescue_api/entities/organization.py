from datetime import datetime

from rescue_api.entities.base_entity import BaseRescueModel


class Organization(BaseRescueModel):
    dg_id: str
    dg_name: str
    dg_title: str
    dg_created: datetime
