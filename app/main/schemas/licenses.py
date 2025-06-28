from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime, date

from app.main.schemas import OrganisationSlim, ServiceOut, AddedBySlim, OrganisationWithOwner, UserOut


class LicenceBase(BaseModel):
    organization_uuid:str
    service_uuid:str
    licence_duration_uuid:str


class LicenceCreate(LicenceBase):
    pass

class LicenceUpdate(LicenceBase):
    uuid:str
    organization_uuid:Optional[str]
    service_uuid:Optional[str]
    licence_duration_uuid:Optional[str]



class OrganisationWithOwner(BaseModel):
    uuid: str
    name: Optional[str]
    email: Optional[str]
    phone_number: Optional[str]
    description: Optional[str]
    owner: Optional[UserOut]  # <- relation vers le user
    model_config = ConfigDict(from_attributes=True)

class LicenceDurationSlim(BaseModel):
    uuid: str
    key: Optional[str]
    duration_days: int
    description: Optional[str]
    model_config = ConfigDict(from_attributes=True)

class Licence(BaseModel):
    uuid:str
    organisation: Optional[OrganisationWithOwner] = None  # 👈 ici
    service:Optional[ServiceOut]=None
    licence_duration:Optional[LicenceDurationSlim]=None
    license_key:Optional[str]=None
    status:Optional[str]=None
    encrypted_data:Optional[str]=None
    creator: Optional[AddedBySlim]=None
    expires_at:Optional[datetime]=None
    is_expired : Optional[bool]=False
    model_config = ConfigDict(from_attributes=True)


class LicenceResponseList(BaseModel):
    total: int
    pages: int
    per_page: int
    current_page: int
    data: list[Licence]

    model_config = ConfigDict(from_attributes=True)


class LicenceSlim(BaseModel):
    uuid:str
    organisation: Optional[OrganisationWithOwner] = None  # 👈 ici
    service:Optional[ServiceOut]=None
    licence_duration:Optional[LicenceDurationSlim]=None
    license_key:Optional[str]=None
    status:Optional[str]=None
    encrypted_data:Optional[str]=None
    model_config = ConfigDict(from_attributes=True)

class ActivedLicence(BaseModel):
    licence_uuid:str
    service_uuid:str
    encrypted_data:str


class RenouvelLicence(BaseModel):
    uuid:str
    new_start_date:date

class DeleteLicence(BaseModel):
    uuid:str

class ProlongedLicence(BaseModel):
    uuid:str
    number_of_days : int


class LicenceDelete(BaseModel):
    uuid:str

