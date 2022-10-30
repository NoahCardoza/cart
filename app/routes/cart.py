from app import models, schemas, security
from app.database import get_database
from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

cart_router = APIRouter()

async def get_user_current_order(db: AsyncSession = Depends(get_database), user: schemas.user.UserContext = Depends(security.get_current_user)) -> models.Order:
    """Get the current order for the user or create one if it doesn't exist.

    Args:
        db (AsyncSession): The database session.
        user UserContext: The currently logged user context.

    Returns:
        models.Order: The current order for the user.
    """
    cart = (await db.execute(
        select(models.Order).where(models.Order.user_id == user.id and models.Order.status == models.OrderStatus.CART)
    )).scalars().first()

    if cart is None:
        cart = models.Order(user_id=user.id, status=models.OrderStatus.CART)
        db.add(cart)
        await db.commit()
        await db.refresh(cart)
    return cart


@cart_router.get("/", response_model=schemas.order.OrderCartOut)
async def get_cart(cart: models.Order = Depends(get_user_current_order)):
    """Get the current users cart items."""
    return cart

@cart_router.post("/", response_model=schemas.order.OrderItemOut)
async def add_to_cart(
        item: schemas.product.ProductCartItemIn,
        cart: models.Order = Depends(get_user_current_order),
        db: AsyncSession = Depends(get_database)
    ):
    """Add an item to the current users cart."""
    
    product = (await db.execute(select(models.Product).where(models.Product.id == item.product_id))).scalars().first()
    product.quantity -= item.quantity 
    
    if (product.quantity < 0):
        raise HTTPException(status_code=400, detail="Not enough stock")

    order_item = (await db.execute(select(models.OrderItem).where(
        models.OrderItem.product_id == item.product_id and models.OrderItem.order_id == cart.id
    ))).scalars().first()
    if order_item is None:
        order_item = models.OrderItem(product_id=item.product_id, order_id=cart.id, quantity=item.quantity)
        db.add(order_item)
    else:
        order_item.quantity += item.quantity
    
    await db.commit()
    await db.refresh(cart)

    return order_item

@cart_router.patch("/{item_id}", response_model=schemas.order.OrderItemOut)
async def update_cart_item(
        item_id: int,
        item: schemas.product.ProductCartItemUpdate,
        cart: models.Order = Depends(get_user_current_order),
        db: AsyncSession = Depends(get_database)
    ):
    """Add an item to the current users cart."""

    order_item = (await db.execute(select(models.OrderItem).where(
        models.OrderItem.id == item_id and models.OrderItem.order_id == cart.id
    ))).scalars().first()

    if order_item is None:
        raise HTTPException(status_code=404, detail="Cart item was not found")

    quantity_diff = order_item.quantity - item.quantity
    order_item.quantity = item.quantity
    order_item.product.quantity += quantity_diff

    if (order_item.product.quantity < 0):
        raise HTTPException(status_code=400, detail="Not enough stock")
    
    await db.commit()
    await db.refresh(order_item)

    return order_item


@cart_router.delete("/{item_id}", status_code=204)
async def delete_cart_item(
        item_id: int,
        cart: models.Order = Depends(get_user_current_order),
        db: AsyncSession = Depends(get_database)
    ):
    """Delete an item from the current users cart."""

    order_item = (await db.execute(select(models.OrderItem).where(
        models.OrderItem.id == item_id and models.OrderItem.order_id == cart.id
    ))).scalars().first()

    if order_item is None:
        raise HTTPException(status_code=404, detail="Cart item was not found")

    order_item.product.quantity += order_item.quantity
    
    await db.delete(order_item)
    await db.commit()
    await db.refresh(cart)
