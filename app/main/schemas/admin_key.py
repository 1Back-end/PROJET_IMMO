from pydantic import BaseModel


class AdminKey(BaseModel):
    key: str
