# coding: utf-8

from datetime import datetime

from rescue_api.database import Base
from sqlalchemy import text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class DatasetRanking(Base):
    __tablename__ = "dataset_rankings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    comment: Mapped[str]
    ranking_date: Mapped[datetime]
    type: Mapped[str]

    created_at: Mapped[datetime] = mapped_column(
        server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=text("CURRENT_TIMESTAMP"), onupdate=text("NOW()")
    )

    # Relationships
    ranks = relationship("DatasetRank", back_populates="ranking")
