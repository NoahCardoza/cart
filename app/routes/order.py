from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi_pagination import Page, add_pagination
from fastapi_pagination.ext.async_sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.database import get_database
from app.security import get_current_user

order_router = APIRouter()

@order_router.get("/", response_model=Page[schemas.order.OrderOut])
async def get_all_past_orders(
        user: models.User = Depends(get_current_user),
        db: AsyncSession = Depends(get_database)
    ):
    """List all past orders. Does not include current order."""

    stmt = select(models.Order).where(
        (models.Order.user_id == user.id) & (models.Order.status != models.OrderStatus.CART)
    ).order_by(models.Order.updated_at.desc())

    return await paginate(db, stmt)

@order_router.get("/{order_id}/", response_model=schemas.order.OrderOut, response_model_exclude_none=True)
async def get_order_by_id(
        order_id: int,
        user: models.User = Depends(get_current_user),
        db: AsyncSession = Depends(get_database)
    ):
    """Get a past order by ID. Only the user who placed the order can access it."""
    
    stmt = select(models.Order).where((models.Order.id == order_id) & (models.Order.user_id == user.id))

    order = (await db.execute(stmt)).scalars().first()

    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    return order

add_pagination(order_router)