from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class CountrywithCityBase(BaseModel):
    name: str
    code: str

class CountryWithCreate(CountrywithCityBase):
    pass
class CountryWithUpdate(CountrywithCityBase):
    pass


class CountryWithOut(CountrywithCityBase):
    uuid: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class CityBase(BaseModel):
    name: str
    latitude: float
    longitude: float
    altitude: float

class CityCreate(CityBase):
    country_uuid: str

class CityOut(CityBase):
    uuid: str
    created_at: datetime
    updated_at: datetime
    country: Optional[CountryWithOut]
    model_config = ConfigDict(from_attributes=True)

class CitySlim(BaseModel):
    uuid: str
    name: str
    latitude: float
    longitude: float
    altitude: float
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class CountryResponseList(BaseModel):
    total: int
    pages: int
    per_page: int
    current_page: int
    data: list[CityOut]  # ✅ Liste de villes avec pays

    model_config = ConfigDict(from_attributes=True)


class CountrySlim(BaseModel):
    uuid: str
    code : str
    name : str
    created_at : Optional[datetime]
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)

class CountryResponseListSlim(BaseModel):
    total: int
    pages: int
    per_page: int
    current_page: int
    data: list[CountrySlim]

    model_config = ConfigDict(from_attributes=True)