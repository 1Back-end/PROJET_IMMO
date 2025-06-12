from fastapi_pagination.default import Params as BaseParams
from fastapi import Query


class CustomParams(BaseParams):
    size: int = Query(10, ge=1, le=100000, description="Page size")
