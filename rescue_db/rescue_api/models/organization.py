from datetime import datetime

from rescue_api.database import Base
from sqlalchemy import text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    dg_id: Mapped[str] = mapped_column(unique=True, nullable=False)
    dg_name: Mapped[str]
    dg_title: Mapped[str]
    dg_created: Mapped[datetime]
    created_at: Mapped[datetime] = mapped_column(server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime] = mapped_column(server_default=text("CURRENT_TIMESTAMP"), onupdate=text("NOW()"))

    datasets = relationship("Dataset", back_populates="organization", cascade="all, delete-orphan")
