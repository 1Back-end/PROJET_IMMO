from pydantic import BaseModel


class Msg(BaseModel):
    message: str


class BoolStatus(BaseModel):
    status: bool


class DataDisplay(BaseModel):
    data: str
