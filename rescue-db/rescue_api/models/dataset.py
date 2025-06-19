from datetime import datetime

from rescue_api.database import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class Dataset(Base):
    __tablename__ = "datasets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    dg_id: Mapped[str]
    dg_organization_id: Mapped[str]
    dg_name: Mapped[str]
    dg_title: Mapped[str]
    dg_notes: Mapped[str]
    dg_metadata_created: Mapped[datetime]
    dg_metadata_modified: Mapped[datetime]
    access_direct_dl_count: Mapped[int]
    access_total_count: Mapped[int]
    dg_created: Mapped[datetime]
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]
