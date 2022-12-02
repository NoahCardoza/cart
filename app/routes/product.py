from typing import Any, List, Optional

from app import models, schemas
from app.database import get_database
from app.dependencies.field_expansion import FieldExpansionQueryParams
from app.security import get_current_employee
from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

product_router = APIRouter()

@product_router.patch("/{product_id}")
async def update_product(
    product_id: int,
    new_product_info: schemas.product.ProductUpdate,
    user: schemas.user.UserContext = Depends(get_current_employee), # throws 401 if not logged in as an employee
    db: AsyncSession = Depends(get_database)
):
    item_update = (await db.execute(select(models.Product).where(
        models.Product.id == product_id
    ))).scalars().first()

    if item_update is None:
        raise HTTPException(status_code=404, detail="Product not found")

    item_update.quantity = new_product_info.quantity
    item_update.price = new_product_info.price

    await db.commit()
    await db.refresh(item_update)

    return item_update


@product_router.get("/{slug}", response_model=schemas.product.ProductOut, response_model_exclude_none=True)
async def get_product_by_slug(
    slug: str,
    expansions: Optional[List[Any]] = Depends(FieldExpansionQueryParams({
        'category': selectinload(models.Product.category)
    })),
    db: AsyncSession = Depends(get_database)
):
    """Get a product by it's slug."""
    stmt = select(models.Product).where(models.Product.slug == slug)

    if expansions:
        stmt = stmt.options(*expansions)

    product = (await db.execute(stmt)).scalars().first()

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return product
