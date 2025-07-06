from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class LicenceDurationModel(BaseModel):
    uuid:str
    key:str
    duration_days:int
    description:Optional[str]
    price:Optional[float]
    is_active:bool
    created_at:datetime
    updated_at:datetime
    model_config = ConfigDict(from_attributes=True)

class LicenceDurationCrete(BaseModel):
    key: str
    duration_days: int
    description: Optional[str]
    price: Optional[float]



class LicenceDurationUpdate(BaseModel):
    uuid:str
    key: Optional[str]
    duration_days:int
    price: Optional[float]
    description:Optional[str]


class LicenceDurationSlim(BaseModel):
    uuid: str
    key: Optional[str]
    duration_days: int
    description: Optional[str]
    price: Optional[float]
    model_config = ConfigDict(from_attributes=True)


class LicenceDurationUpdateStatus(BaseModel):
    uuid:str
    is_active:bool

class LicenceDurationDelete(BaseModel):
    uuid:str

class LicenceDurationModelList(BaseModel):
    total: int
    pages: int
    per_page: int
    current_page:int
    data: list[LicenceDurationModel]

    model_config = ConfigDict(from_attributes=True)