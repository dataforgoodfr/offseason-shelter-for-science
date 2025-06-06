from datetime import datetime
from typing import Optional

import requests
from pydantic import BaseModel, HttpUrl


class DataGovData(BaseModel):
    id: str
    name: str
    description: str
    locator_function: Optional[str] = None
    locator_protocol: Optional[str] = None
    url: HttpUrl
    created: datetime
    metadata_modified: datetime
    dataset_id: str
    state: str  # Could be literal if list is known
    mimetype: Optional[str] = None


class HeadRequestInfo(BaseModel):
    request_worked: bool
    content_length: Optional[int] = None
    content_type: Optional[str] = None


class Resource(BaseModel):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    dg_data: DataGovData

    @classmethod
    def from_nocodb_dict(cls, data: dict):
        dg_data = DataGovData(
            id=data["dg_id"],
            name=data["dg_name"],
            description=data["dg_description"],
            locator_function=data["dg_locator_function"],
            locator_protocol=data["dg_locator_protocol"],
            url=data["dg_url"],
            created=data["dg_created"],
            metadata_modified=data["dg_metadata_modified"],
            dataset_id=data["dg_dataset_id"],
            state=data["dg_state"],
            mimetype=data["dg_mimetype"],
        )
        return cls(
            id=data["Id"],
            created_at=data["CreatedAt"],
            updated_at=data["UpdatedAt"],
            dg_data=dg_data,
        )

    def retrieve_head_info(self) -> HeadRequestInfo:
        try:
            response = requests.head(self.dg_data.url, timeout=0.5)
            response.raise_for_status()
        except Exception:
            return HeadRequestInfo(request_worked=False)
        return HeadRequestInfo(
            request_worked=True,
            content_length=(
                int(response.headers["Content-Length"])
                if "Content-Length" in response.headers.keys()
                else None
            ),
            content_type=(
                response.headers["Content-Type"]
                if "Content-Type" in response.headers.keys()
                else None
            ),
        )
