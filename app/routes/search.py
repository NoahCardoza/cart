from typing import Any, List, Optional

from app import models
from app.database import get_database
from app.dependencies.field_expansion import FieldExpansionQueryParams
from app.dependencies.pagination import PaginationQueryParams
from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

search_router = APIRouter()


@search_router.get("/")
async def search(
    q: str = Query(
        default=...,
        description="The search query.",
        max_length=20
    ),
    pagination: PaginationQueryParams = Depends(),
    expansions: Optional[List[Any]] = Depends(FieldExpansionQueryParams({
        'category': selectinload(models.Product.category)
    })),
    db: AsyncSession = Depends(get_database)
):
    """Returns a list of products that match the search query in their name or description field

    Exapndable fields:
        - category
    """

    stmt = select(models.Product).where(
        or_(
            models.Product.name.ilike(f"%{q}%"),
            models.Product.description.ilike(f"%{q}%")
        )
    ).limit(pagination.limit).offset((pagination.page-1)*pagination.limit)

    if expansions:
        stmt = stmt.options(*expansions)

    results = await db.execute(stmt)

    return results.scalars().all()
