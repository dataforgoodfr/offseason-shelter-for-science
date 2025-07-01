# coding: utf-8

from rescue_api.entities.base_entity import BaseRescueModel


class DatasetJson(BaseRescueModel):
    dataset_id: str
    content: str
