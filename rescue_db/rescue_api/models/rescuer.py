from datetime import datetime
from typing import List

from rescue_api.database import Base
from sqlalchemy import text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .rescues import rescues


class Rescuer(Base):
    __tablename__ = "rescuers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=text("CURRENT_TIMESTAMP"), onupdate=text("NOW()")
    )

    # Relationships
    assets: Mapped[List["Asset"]] = relationship(secondary=rescues, back_populates="rescuers")
