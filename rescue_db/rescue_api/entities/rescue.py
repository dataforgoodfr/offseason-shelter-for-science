from rescue_api.entities.base_entity import BaseRescueModel


class Rescue(BaseRescueModel):
    asset_id: int
    rescuer_id: int
    magnet_link: str
    status: str
