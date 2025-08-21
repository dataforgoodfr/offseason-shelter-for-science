from rescue_api.database import Base
from sqlalchemy import Table, Column, BigInteger, Integer, ForeignKey, DateTime, UniqueConstraint, text, Text, Enum
from enum import Enum as PyEnum


class Status(PyEnum):
    success = "SUCCESS"
    fail = "FAIL"


rescues = Table(
    "rescues",
    Base.metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("asset_id", Integer, ForeignKey("assets.id")),
    Column("rescuer_id", Integer, ForeignKey("rescuers.id")),
    Column("magnet_link", Text, nullable=False),
    Column("status", Enum(Status), nullable=False),
    Column("created_at", DateTime, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", DateTime, server_default=text("CURRENT_TIMESTAMP"), onupdate=text("NOW()")),
    UniqueConstraint("asset_id", "rescuer_id")
)