from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

from app.main.schemas import ServiceOut, LicenceDurationSlim, UserOut, LicenceSlim


class LicenceRequestServiceExtend(BaseModel):
    service_uuid:str
    licence_duration_uuid:str
    description:Optional[str]
    licence_uuid:str

class LicenceRequestService(BaseModel):
    service_uuid:str
    licence_duration_uuid:str
    description:Optional[str]


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
    licence : Optional[LicenceSlim] = None
    creator: Optional[UserOut]=None
    status: str
    description:Optional[str]
    type:Optional[str]
    created_at: datetime
    updated_at: datetime
    is_accepted: Optional[bool]
    is_prolonged: Optional[bool]
    counter_generation : Optional[int]
    counter_prolongation : Optional[int]

    model_config = ConfigDict(from_attributes=True)



class LicenceRequestServiceResponseList(BaseModel):
    total: int
    pages: int
    per_page: int
    current_page:int
    data: list[LicenceRequestServiceResponse]

    model_config = ConfigDict(from_attributes=True)


