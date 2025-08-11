from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from datetime import datetime

from app.main.schemas import AddedBy, OrganisationOwnerServiceOut
from app.main.schemas.contry_with_city import CountrySlim, CitySlim


class OrganisationBase(BaseModel):
    owner_first_name :str
    owner_last_name :str
    owner_email :str
    owner_phone_number :Optional[str]=None
    owner_password :str

    company_name :str
    company_email :str
    company_phone_number :Optional[str]=None
    company_description :Optional[str]=None

    additional_information : Optional[str]=None


    country_uuid : Optional[str]=None
    city_uuid : Optional[str]=None


class OrganisationCreate(OrganisationBase):
    service_uuids: List[str]


class OrganisationValidateAccount(BaseModel):
    email: str
    code_otp:str


class OrgansationToDelete(BaseModel):
    email: str


class OrganisationToValidateAccountSlim1(BaseModel):
    uuid: str
    email: str
    code: str

class OrganisationUpdate(BaseModel):
    company_name: Optional[str] = None
    company_email: Optional[str] = None
    company_phone_number: Optional[str] = None
    company_description: Optional[str] = None

    country_uuid: Optional[str] = None
    city_uuid: Optional[str] = None
    additional_information : Optional[str] = None


class OrganisationOut(BaseModel):
    uuid: str
    name: str
    email: str
    phone_number: str
    description: Optional[str]
    country: Optional[CountrySlim]
    city : Optional[CitySlim]
    owner: Optional[AddedBy]
    owner_services: List[OrganisationOwnerServiceOut]  # <-- liste de rel linkée au service
    status: str
    additional_information: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class OrganisationResponseList(BaseModel):
    total: int
    pages: int
    per_page: int
    current_page: int
    data: list[OrganisationOut]

    model_config = ConfigDict(from_attributes=True)


class OrganisationUpdateStatus(BaseModel):
    uuid:str
    status : str


class OrganisationSlim(BaseModel):
    uuid: str
    name:str
    email:str
    model_config = ConfigDict(from_attributes=True)


class OrganisationDelete(BaseModel):
    uuid:str
