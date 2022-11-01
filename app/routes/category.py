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

category_router = APIRouter()


@category_router.post("/")
async def create(
    data: schemas.category.CategoryIn,
    db: AsyncSession = Depends(get_database)
):
    cat = models.Category(**data.dict())
    db.add(cat)

    # stmt = select(models.Product).where(
    #     or_(
    #         models.Product.name.ilike(f"%{q}%"),
    #         models.Product.description.ilike(f"%{q}%")
    #     )
    # )

    # results = await paginate(db, stmt)
    # print('page', results.items)
    # return results
    return data


add_pagination(category_router)
