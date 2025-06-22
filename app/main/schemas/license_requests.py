from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

from app.main.schemas import AddedBySlim


class LicenseRequest(BaseModel):
    title: str
    description: str

class LicenceRequestCreate(LicenseRequest):
    pass

class LicenseResponse(BaseModel):
    uuid: str
    title: str
    description: str
    is_read: bool
    sender : Optional[AddedBySlim]
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class LicenceRequestResponseList(BaseModel):
    total: int
    pages: int
    per_page: int
    current_page:int
    data: list[LicenseResponse]

    model_config = ConfigDict(from_attributes=True)


class LicenceRequestIsRead(BaseModel):
    uuid: str