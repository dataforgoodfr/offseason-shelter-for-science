from rescue_api.entities.base_entity import BaseRescueModel


class Rescuer(BaseRescueModel):
    name: str
    description: str
