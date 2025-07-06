from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

from app.main.schemas import ServiceOut, LicenceDurationSlim, UserOut


class LicenceRequestService(BaseModel):
    service_uuid:str
    licence_duration_uuid:str
    description:Optional[str]
    type:Optional[str]


class LicenceRequestCreate(LicenceRequestService):
    pass


class LicenceRequestUpdate(BaseModel):
    uuid:str
    licence_duration_uuid:Optional[str]
    service_uuid:Optional[str]
    description:Optional[str]
    type:Optional[str]


class LicenceRequestServiceResponse(BaseModel):
    uuid:str
    service: Optional[ServiceOut] = None
    licence_duration: Optional[LicenceDurationSlim] = None
    creator: Optional[UserOut]=None
    status: str
    description:Optional[str]
    type:Optional[str]
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)



class LicenceRequestServiceResponseList(BaseModel):
    total: int
    pages: int
    per_page: int
    current_page:int
    data: list[LicenceRequestServiceResponse]

    model_config = ConfigDict(from_attributes=True)


