from app import models, schemas
from app.database import get_database
from app.security import get_current_employee
from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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

