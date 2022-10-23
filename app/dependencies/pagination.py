from fastapi import Query
from pydantic import BaseModel


class PaginationQueryParams(BaseModel):
    limit: int = Query(
        default=10,
        description="The number of results to return per page.",
        le=20,
        ge=1,
    )
    page: int = Query(
        default=1,
        ge=1,
        description="The page number to return."
    )
