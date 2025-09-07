from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from datetime import datetime

from app.main.schemas import AddedBySlim, FileSlim2, OwnerHasUser


class LicenseRequest(BaseModel):
    title: str
    description: str
    type: str

class LicenceRequestCreate(LicenseRequest):
    pass



class OrganisationSlim(BaseModel):
    uuid: str
    name: str
    model_config = ConfigDict(from_attributes=True)


class OrganisationWithOwner(BaseModel):
    uuid: str
    name: str
    owner : OwnerHasUser

class UserOut(BaseModel):
    first_name: str
    last_name: str
    role: str
    phone_number: Optional[str] = None
    avatar: Optional[FileSlim2] = None
    organisations:Optional[OrganisationSlim]=None  # ✅ correction ici

    model_config = ConfigDict(from_attributes=True)




class LicenseResponse(BaseModel):
    uuid: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    is_read: Optional[bool] = None
    type: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    owner: Optional[UserOut] = None
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


class LicenceRequestUpdateStatus(BaseModel):
    uuid: str
    status: str


class LicenceRequestCancel(BaseModel):
    request_uuid: str
    code:Optional[str]
