# coding: utf-8

from datetime import datetime

from rescue_api.database import Base
from sqlalchemy import ForeignKey, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship


class DatasetJson(Base):
    __tablename__ = "datasets_json"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    dataset_id: Mapped[int] = mapped_column(
        ForeignKey("datasets.id"), unique=True, nullable=False
    )
    content: Mapped[str] = mapped_column(JSONB, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=text("CURRENT_TIMESTAMP"), onupdate=text("NOW()")
    )

    # Relationships
    dataset = relationship("Dataset", uselist=False, back_populates="json_data")
