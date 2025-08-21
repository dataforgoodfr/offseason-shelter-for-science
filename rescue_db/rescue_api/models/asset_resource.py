from rescue_api.database import Base
from sqlalchemy import Table, Column, BigInteger, Integer, ForeignKey, DateTime, UniqueConstraint, text


asset_resource = Table(
    "asset_resource",
    Base.metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("asset_id", Integer, ForeignKey("assets.id"), nullable=False),
    Column("resource_id", Integer, ForeignKey("resources.id"), nullable=False),
    Column("created_at", DateTime, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", DateTime, server_default=text("CURRENT_TIMESTAMP"), onupdate=text("NOW()")),
    UniqueConstraint("asset_id", "resource_id")
)