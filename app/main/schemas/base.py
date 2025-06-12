from pydantic import BaseModel, ConfigDict
from typing import Any, List


class DataList(BaseModel):
    total: int
    pages: int
    current_page: int
    per_page: int
    data: List[Any] = []

    model_config = ConfigDict(from_attributes=True)

