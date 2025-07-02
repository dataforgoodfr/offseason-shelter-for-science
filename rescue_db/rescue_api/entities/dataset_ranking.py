# coding: utf-8

from datetime import datetime

from rescue_api.entities.base_entity import BaseRescueModel


class DatasetRanking(BaseRescueModel):
    name: str
    comment: str
    ranking_date: datetime
    type: str