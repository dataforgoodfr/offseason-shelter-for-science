from datetime import datetime

from rescue_api.database import Base
from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class AssetKind(Base):
    __tablename__ = "asset_kinds"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    url: Mapped[str]
    kind_id: Mapped[int] = mapped_column(ForeignKey("asset_kinds.id"))
    resource_id: Mapped[int] = mapped_column(ForeignKey("resources.id"))
    created_at: Mapped[datetime] = mapped_column(server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime] = mapped_column(server_default=text("CURRENT_TIMESTAMP"), onupdate=text("NOW()"))

    # Relationships
    resource = relationship("Resource", back_populates="assets")
