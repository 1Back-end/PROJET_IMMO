from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

from app.main.schemas import AddedBySlim


class ServiceBase(BaseModel):
    name : str
    description : Optional[str]

class ServiceCreate(ServiceBase):
    pass

class ServiceUpdate(BaseModel):
    uuid:str
    name : Optional[str]
    description: Optional[str]

class ServiceDelete(BaseModel):
    uuid:str

class ServiceUpdateStatus(BaseModel):
    uuid: str
    status: str

class ServiceOut(BaseModel):
    uuid: str
    name: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class OrganisationOwnerServiceOut(BaseModel):
    service: ServiceOut
    model_config = ConfigDict(from_attributes=True)

class Service(BaseModel):
    uuid:str
    name: str
    description: Optional[str]
    created_at : datetime
    updated_at : Optional[datetime]
    creator : Optional[AddedBySlim]
    model_config = ConfigDict(from_attributes=True)


class ServiceSlim1(BaseModel):
    uuid: str
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)

class ServiceResponseList(BaseModel):
    total: int
    pages: int
    per_page: int
    current_page: int
    data: list[Service]

    model_config = ConfigDict(from_attributes=True)