from typing import Any, List, Optional

from app import models, schemas
from app.database import get_database
from app.dependencies.field_expansion import FieldExpansionQueryParams
from fastapi import APIRouter, Depends, Query
from fastapi_pagination import Page, add_pagination
from fastapi_pagination.ext.async_sqlalchemy import paginate
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

search_router = APIRouter()


@search_router.get("/", response_model=Page[schemas.product.ProductOut], response_model_exclude_none=True)
async def search(
    q: str = Query(
        default=...,
        description="The search query.",
        max_length=20
    ),
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
    ).order_by(models.Product.slug.asc())

    if expansions:
        stmt = stmt.options(*expansions)
    results = await paginate(db, stmt)

    return results


add_pagination(search_router)

