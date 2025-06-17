from datetime import datetime

from rescue_api.database import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class Resource(Base):
    __tablename__ = "resources"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    dg_id: Mapped[str]
    dg_name: Mapped[str]
    dg_description: Mapped[str]
    dg_resource_locator_function: Mapped[str]
    dg_resource_locator_protocol: Mapped[str]
    dg_mimetype: Mapped[str]
    dg_state: Mapped[str]
    dg_created: Mapped[datetime]
    dg_metadata_modified: Mapped[datetime]
    dg_url: Mapped[str]
    resource_type: Mapped[str]
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.id"))
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]
