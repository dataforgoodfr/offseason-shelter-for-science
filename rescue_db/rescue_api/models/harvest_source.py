# coding: utf-8

from datetime import datetime

from rescue_api.database import Base
from sqlalchemy import BigInteger, ForeignKey, text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship


class HarvestSourceType(Base):
    __tablename__ = "harvest_source_types"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=text("CURRENT_TIMESTAMP"), onupdate=text("NOW()")
    )

    # Relationships
    # harvest_sources = relationship("HarvestSource", back_populates="harvest_source_type")


class HarvestFrequency(Base):
    __tablename__ = "harvest_frequencies"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=text("CURRENT_TIMESTAMP"), onupdate=text("NOW()")
    )


class HarvestSource(Base):
    __tablename__ = "harvest_sources"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    dg_id: Mapped[str] = mapped_column(unique=True, nullable=False)
    dg_name: Mapped[str]
    dg_title: Mapped[str]
    dg_source: Mapped[str]
    dg_created: Mapped[datetime]
    dg_total_datasets: Mapped[int]
    harvest_source_type_id: Mapped[int] = mapped_column(
        ForeignKey("harvest_source_types.id")
    )
    harvest_frequency_id: Mapped[int] = mapped_column(
        ForeignKey("harvest_frequencies.id")
    )
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))

    created_at: Mapped[datetime] = mapped_column(
        server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=text("CURRENT_TIMESTAMP"), onupdate=text("NOW()")
    )

    # Relationships
    # harvest_source_type = relationship("HarvestSourceType", back_populates="harvest_sources")


class HarvestSourceDataset(Base):
    __tablename__ = "harvest_source_dataset"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    harvest_source_id: Mapped[int] = mapped_column(ForeignKey("harvest_sources.id"))
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.id"))

    __table_args__ = (
        UniqueConstraint(
            "harvest_source_id", "dataset_id", name="uq_harvest_source_dataset"
        ),
    )
