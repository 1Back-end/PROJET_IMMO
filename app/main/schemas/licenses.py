from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

from app.main.schemas import OrganisationSlim, ServiceOut, AddedBySlim


class LicenceBase(BaseModel):
    organization_uuid:str
    service_uuid:str
    start_date:datetime
    end_date:datetime

class LicenceCreate(LicenceBase):
    pass

class LicenceUpdate(LicenceBase):
    uuid:str
    organization_uuid:Optional[str]
    service_uuid:Optional[str]
    start_date:Optional[datetime]
    end_date:Optional[datetime]


class Licence(BaseModel):
    uuid:str
    organization:Optional[OrganisationSlim]=None
    service:Optional[ServiceOut]=None
    start_date:Optional[datetime]=None
    end_date:Optional[datetime]=None
    license_key:Optional[str]=None
    status:Optional[str]=None
    encrypted_data:Optional[str]=None
    creator: Optional[AddedBySlim]
    model_config = ConfigDict(from_attributes=True)


class LicenceResponseList(BaseModel):
    total: int
    pages: int
    per_page: int
    current_page: int
    data: list[Licence]

    model_config = ConfigDict(from_attributes=True)


class ActivedLicence(BaseModel):
    uuid:str
    service_uuid:str


class RenouvelLicence(BaseModel):
    uuid:str
    new_start_date:datetime