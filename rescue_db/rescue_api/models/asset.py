from datetime import datetime
from typing import List

from rescue_api.database import Base
from sqlalchemy import BigInteger, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .asset_resource import asset_resource


class AssetKind(Base):
    __tablename__ = "asset_kinds"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=text("CURRENT_TIMESTAMP"), onupdate=text("NOW()")
    )


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    url: Mapped[str] = mapped_column(unique=True, nullable=False, index=True)
    kind_id: Mapped[int] = mapped_column(ForeignKey("asset_kinds.id"))
    size: Mapped[int] = mapped_column(BigInteger, nullable=True)
    mtime: Mapped[datetime] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=text("CURRENT_TIMESTAMP"), onupdate=text("NOW()")
    )

    # Relationships
    resources: Mapped[List["Resource"]] = relationship(secondary=asset_resource, back_populates="assets")
