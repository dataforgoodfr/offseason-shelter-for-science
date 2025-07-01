from datetime import datetime

from rescue_api.database import Base
from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Dataset(Base):
    __tablename__ = "datasets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    dg_id: Mapped[str] = mapped_column(unique=True, nullable=False)
    dg_name: Mapped[str]
    dg_title: Mapped[str]
    dg_notes: Mapped[str]
    dg_metadata_created: Mapped[datetime]
    dg_metadata_modified: Mapped[datetime]
    access_direct_dl_count: Mapped[int]
    access_total_count: Mapped[int]
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))
    created_at: Mapped[datetime] = mapped_column(server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime] = mapped_column(server_default=text("CURRENT_TIMESTAMP"), onupdate=text("NOW()"))

    # Relationships
    organization = relationship("Organization", back_populates="datasets")
    resources = relationship("Resource", back_populates="dataset", cascade="all, delete-orphan")

    json_data = relationship("DatasetJson", uselist=False, back_populates="dataset", cascade="all, delete-orphan")
