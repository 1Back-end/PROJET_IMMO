from typing import Any

from pydantic import BaseModel


class Msg(BaseModel):
    message: str


class BoolStatus(BaseModel):
    status: bool


class DataDisplay(BaseModel):

    data: str
class MsgWithData(BaseModel):
    message: str
    data: Any  # ou un modèle plus précis OrganisationRead ou similaire