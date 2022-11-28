import functools
from datetime import datetime

import stripe
from fastapi import APIRouter, Depends, Request
from fastapi.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas, security
from app.database import get_database
from app.environ import BASE_URL_UI
from app.stripe_config import shipping_options

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
        select(models.Order).where((models.Order.user_id == user.id) & (models.Order.status == models.OrderStatus.CART))
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
        (models.OrderItem.product_id == item.product_id) & (models.OrderItem.order_id == cart.id)
    ))).scalars().first()
    if order_item is None:
        order_item = models.OrderItem(product_id=item.product_id, order_id=cart.id, quantity=item.quantity)
        db.add(order_item)
    else:
        order_item.quantity += item.quantity
    
    cart.updated_at = datetime.utcnow()        
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
        (models.OrderItem.id == item_id) & (models.OrderItem.order_id == cart.id)
    ))).scalars().first()
    
    if order_item is None:
        raise HTTPException(status_code=404, detail="Cart item was not found")

    quantity_diff = order_item.quantity - item.quantity
    order_item.quantity = item.quantity
    order_item.product.quantity += quantity_diff

    if (order_item.product.quantity < 0):
        raise HTTPException(status_code=400, detail="Not enough stock")
    
    cart.updated_at = datetime.utcnow()
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
        (models.OrderItem.id == item_id) & (models.OrderItem.order_id == cart.id)
    ))).scalars().first()

    if order_item is None:
        raise HTTPException(status_code=404, detail="Cart item was not found")

    order_item.product.quantity += order_item.quantity
    cart.updated_at = datetime.utcnow()
    
    await db.delete(order_item)
    await db.commit()
    await db.refresh(cart)


@cart_router.get("/", response_model=schemas.order.OrderCartOut)
async def get_user_past_order(db: AsyncSession = Depends(get_database), user: schemas.user.UserContext = Depends(security.get_current_user)) -> models.Order:
   
    cart = (await db.execute(
        select(models.Order).where(
            (models.Order.user_id == user.id) & (models.Order.status != models.OrderStatus.CART)
        )
    )).scalars().first()

    return cart


@cart_router.post("/checkout/")
async def checkout_cart(
        user: schemas.user.UserContext = Depends(security.get_current_user),
        cart: models.Order = Depends(get_user_current_order),
    ):
    """Checkout the current users cart."""

    total_weight = functools.reduce(float.__add__, [item.product.weight * item.quantity for item in cart.items])

    shipping_options = (
        { 'shipping_rate': shipping_options['standard'] },
        { 'shipping_rate': shipping_options['express'] },
    )

    # provide free shipping option for orders over 20 pounds
    if total_weight >= 20:
        shipping_options = (
            { 'shipping_rate': shipping_options['complimentary'] },
            *shipping_options
        )

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        success_url=f"{BASE_URL_UI}/orders/{cart.id}?stripe=success",
        cancel_url=f"{BASE_URL_UI}/shop?expand=cart",
        customer=user.stripe_id,
        metadata={
            "order_id": cart.id
        },
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "tax_behavior": "exclusive",
                    "unit_amount": int(item.product.price * 100),
                    "product_data": {
                        "name": item.product.name,
                        "description": item.product.description,
                        "images": [item.product.image_url],
                    },
                },
                "quantity": item.quantity,
            } for item in cart.items
        ],
        customer_update={
            'shipping': 'auto',
        },
        automatic_tax={
            'enabled': True,
        },
        shipping_address_collection={
            "allowed_countries": ["US"],
        },
        shipping_options=shipping_options,
        mode="payment",
    )

    return { "id": checkout_session.id, "url": checkout_session.url }