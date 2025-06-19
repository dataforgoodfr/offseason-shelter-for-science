from datetime import datetime

from rescue_api.database import Base
from sqlalchemy.orm import Mapped, mapped_column


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    dg_id: Mapped[str]
    dg_name: Mapped[str]
    dg_title: Mapped[str]
    dg_created: Mapped[datetime]
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]
