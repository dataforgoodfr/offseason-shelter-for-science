from datetime import datetime

from rescue_api.database import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class AssetKind(Base):
    __tablename__ = "asset_kinds"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    url: Mapped[str]
    kind_id: Mapped[int] = mapped_column(ForeignKey("asset_kinds.id"))
    resource_id: Mapped[int] = mapped_column(ForeignKey("resources.id"))
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]
