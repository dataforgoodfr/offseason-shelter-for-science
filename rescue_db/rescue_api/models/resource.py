from datetime import datetime
from typing import List
import re
from urllib.parse import urlparse

from rescue_api.database import Base
from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .asset_resource import asset_resource


_FILE_EXT_REGEX = re.compile(r".+\.(tar.[zZ]|[a-zA-Z7][a-zA-Z0-9]+)$")
_OTHER_AUTHORIZED_EXTENSIONS = ["geojson"]
_REJECTED_EXTENSIONS = ["aspx", "htm", "html", "htmlx", "shtml"]


class Resource(Base):
    __tablename__ = "resources"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    dg_id: Mapped[str] = mapped_column(unique=True, nullable=False)
    dg_name: Mapped[str]
    dg_description: Mapped[str]
    dg_resource_locator_function: Mapped[str] = mapped_column(
        "dg_resource_locator_function", nullable=True
    )
    dg_resource_locator_protocol: Mapped[str] = mapped_column(
        "dg_resource_locator_protocol", nullable=True
    )
    dg_mimetype: Mapped[str] = mapped_column("dg_mimetype", nullable=True)
    dg_state: Mapped[str]
    dg_created: Mapped[datetime]
    dg_metadata_modified: Mapped[datetime]
    dg_url: Mapped[str]
    resource_type: Mapped[str]
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.id"))
    created_at: Mapped[datetime] = mapped_column(
        server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=text("CURRENT_TIMESTAMP"), onupdate=text("NOW()")
    )

    # Relationships
    dataset = relationship("Dataset", back_populates="resources")
    assets: Mapped[List["Asset"]] = relationship(secondary=asset_resource, back_populates="resources", cascade="all, delete")

    def set_url(self, url: str):
        self.dg_url = url
        self.resource_type = self.get_type_from_url(url)

    @staticmethod
    def get_type_from_url(url: str) -> str:
        result = None

        if not url or not url.strip():
            return None

        parsed_url = urlparse(url)

        url_path = parsed_url.path.strip()
        if url_path:
            if url_path[-1] == "/" or url_path.endswith("%2F"):
                result = "dir"
            else:
                match_res = _FILE_EXT_REGEX.match(url_path)
                if match_res:
                    ext = match_res.group(1)
                    if (
                        len(ext) <= 5 and ext not in _REJECTED_EXTENSIONS
                    ) or ext in _OTHER_AUTHORIZED_EXTENSIONS:
                        result = ext

        if not result:
            result = "web"

        return result
