# coding: utf-8

from datetime import datetime

from pydantic import BaseModel, Field
from rescue_api.entities.base_entity import BaseRescueModel


class HarvestSourceType(BaseRescueModel):
    name: str


class HarvestFrequency(BaseRescueModel):
    name: str


# CKAN Harvest Source Entity
class HarvestSource(BaseRescueModel):
    dg_id: str
    dg_name: str
    dg_title: str
    dg_source: str
    dg_created: datetime
    dg_total_datasets: int
    harvest_source_type_id: int
    harvest_frequency_id: int
    organization_id: int


class HarvestSourceDataset(BaseModel):
    _id: int = Field(alias="id")
    harvest_source_id: int
    dataset_id: int
