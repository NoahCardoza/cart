from typing import Any, List, Optional

from app import models, schemas
from app.database import get_database
from app.dependencies.field_expansion import FieldExpansionQueryParams
from app.security import get_current_superuser
from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page, add_pagination
from fastapi_pagination.ext.async_sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

category_router = APIRouter()


@category_router.get("/", response_model=Page[schemas.category.CategoryOut])
async def get_all_categories(    
    db: AsyncSession = Depends(get_database)
):
    """List all categories."""
    return await paginate(db, select(models.Category).order_by(models.Category.slug.asc()))


@category_router.get("/{slug}", response_model=schemas.category.CategoryOut, response_model_exclude_none=True)
async def get_category_by_slug(
    slug: str,
    expansions: Optional[List[Any]] = Depends(FieldExpansionQueryParams({
        'products': selectinload(models.Category.products)
    })),
    db: AsyncSession = Depends(get_database)
):
    """Get a category by it's slug."""

    stmt = select(models.Category).where(models.Category.slug == slug)

    if expansions:
        stmt = stmt.options(*expansions)

    category = (await db.execute(stmt)).scalars().first()
    

    if category is None:
        raise HTTPException(status_code=404, detail="Category not found.")
    
    return category


@category_router.post("/", response_model=schemas.category.CategoryOut)
async def create_category(
    data: schemas.category.CategoryIn,
    user: models.User = Depends(get_current_superuser), # gaurd to make sure only superusers can create categories
    db: AsyncSession = Depends(get_database)
):
    """Create a new category."""
    
    category = models.Category(**data.dict())
    existing_category = (await db.execute(select(models.Category).where(models.Category.slug == category.slug))).scalars().first()
    
    if existing_category:
        raise HTTPException(status_code=409, detail="Category will not have a unique slug.")
    
    db.add(category)

    await db.commit()
    await db.refresh(category)
    
    return category


add_pagination(category_router)
