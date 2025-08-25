from datetime import datetime
from typing import List
from enum import Enum

from rescue_api.database import Base
from sqlalchemy import UniqueConstraint, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Status(Enum):
    success = "SUCCESS"
    fail = "FAIL"


class Rescue(Base):
    __tablename__ = "rescues"
    __table_args__ = (
        UniqueConstraint('asset_id', 'rescuer_id', name='rescues_asset_id_rescuer_id_key'),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"))
    rescuer_id: Mapped[int] = mapped_column(ForeignKey("rescuers.id"))
    magnet_link: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[Status] = mapped_column(nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=text("CURRENT_TIMESTAMP"), onupdate=text("NOW()")
    )

    # Relationships
    asset: Mapped["Asset"] = relationship(back_populates="rescuers")
    rescuer: Mapped["Rescuer"] = relationship(back_populates="assets")
