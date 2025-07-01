from datetime import datetime

from pydantic import BaseModel, Field


class BaseRescueModel(BaseModel):
    _id: int = Field(alias="id")
    created_at: datetime
    updated_at: datetime
