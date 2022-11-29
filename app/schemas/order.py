from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.Order import OrderStatus
from app.schemas.product import ProductOut


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

        
class OrderOut(OrderCartOut):
    amount_total: float = Field(..., description="The total amount of the order.", example=42.0)
    amount_subtotal: float = Field(..., description="The subtotal amount of the order.", example=42.0)
    amount_shipping: float = Field(..., description="The shipping amount of the order.", example=42.0)
    amount_tax: float = Field(..., description="The tax amount of the order.", example=42.0)
    latitude: Optional[float] = Field(..., description="The latitude of the shipping address.", example=38.897675)
    longitude: Optional[float] = Field(..., description="The longitude of the shipping address.", example=-77.036547)
    address: str = Field(..., description="The shipping address of the order.", example="238 Blueberry Lane, San Jose")
