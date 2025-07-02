# coding: utf-8

from rescue_api.entities.base_entity import BaseRescueModel


class DatasetRank(BaseRescueModel):
    dataset_id: int
    ranking_id: int
    rank: int
    event_count: int = 0