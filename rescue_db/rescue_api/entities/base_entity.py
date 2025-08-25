from datetime import datetime

from pydantic import BaseModel, Field


class BaseRescueModel(BaseModel):
    id_: int = Field(alias="id")
    created_at: datetime
    updated_at: datetime
