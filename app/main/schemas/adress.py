from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class AddressSlim(BaseModel):
    street: str
    city: str
    state: Optional[str] = None
    zipcode: str
    country: str
    apartment_number: Optional[str] = None
    additional_information: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class AddressBase(BaseModel):
    street: str
    city: str
    state: Optional[str] = None
    zipcode: str
    country: str
    apartment_number: Optional[str] = None
    additional_information: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class AddressCreation(BaseModel):
    city: str
    zipcode: str
    country: str
    model_config = ConfigDict(from_attributes=True)


class Address(AddressBase):
    uuid: str
    date_added: datetime
    date_modified: datetime
    model_config = ConfigDict(from_attributes=True)

class AddressInfo(BaseModel):
    uuid: str

class AddressCreate(AddressBase):
    pass

    model_config = ConfigDict(from_attributes=True)


class AddressUpdate(BaseModel):
    uuid:str
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zipcode: Optional[str] = None
    country: Optional[str] = None
    apartment_number: Optional[str] = None
    additional_information: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

