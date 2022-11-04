from app import models, schemas
from app.database import get_database
from fastapi import APIRouter, Depends
from fastapi_pagination import Page, add_pagination
from fastapi_pagination.ext.async_sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

category_router = APIRouter()


@category_router.get("/", response_model=Page[schemas.category.CategoryOut])
async def get_all_categories(    
    db: AsyncSession = Depends(get_database)
):
    """List all categories."""
    return await paginate(db, select(models.Category))


@category_router.post("/", response_model=schemas.category.CategoryOut)
async def create_category(
    data: schemas.category.CategoryIn,
    db: AsyncSession = Depends(get_database)
):
    """Create a new category."""
    category = models.Category(**data.dict())
    db.add(category)
    await db.commit()
    db.refresh(category)
    return category


add_pagination(category_router)
