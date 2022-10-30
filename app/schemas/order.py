from datetime import datetime
from typing import List

from app.models.Order import OrderStatus
from app.schemas.product import ProductOut
from pydantic import BaseModel, Field


class OrderItemOut(BaseModel):
    id: int = Field(..., description="The order item's ID.", example=420)
    order_id: int = Field(..., description="The order's ID.", example=42)
    quantity: int = Field(..., description="The quantity of the product in the cart.", example=1)
    product: ProductOut = Field(..., description="The product in the order.")

    class Config:
        orm_mode = True

class OrderCartOut(BaseModel):
    id: int = Field(..., description="The cart id.", example=1) 
    status: OrderStatus = Field(..., description="The cart status.", example=OrderStatus.CART)
    updated_at: datetime = Field(..., description="The datetime the cart was updated at.", example="2021-05-01T00:00:00.000000") 
    created_at: datetime = Field(..., description="The datetime the cart was created at.", example="2021-05-01T00:00:00.000000")
    items: List[OrderItemOut] = Field(..., description="The items in the cart.")

    class Config:
        orm_mode = True
