from typing import Optional

from pydantic import BaseModel, Field, conint

from .category import CategoryOut
from .orm import OrmBaseModel


class ProductCartItemUpdate(BaseModel):
    quantity: conint(strict=True, gt=0) = Field(description="The quantity of the product in the cart.", example=1)

class ProductCartItemIn(ProductCartItemUpdate):
    product_id: int = Field(..., description="The product id.", example=1)


class ProductOut(OrmBaseModel):
    id: int = Field(..., description="The product's ID.", example=420)
    category_id: int = Field(...,
                             description="The product's category ID.", example=42)

    slug: str = Field(..., description="The product's slug.",
                      example="eggs-dairy")
    quantity: int = Field(...,
                          description="The amount of stock in our inventory.", example=100)
    weight: float = Field(...,
                          description="The weight of the item.", example=0.3)
    name: str = Field(..., description="The product's name.",
                      example="Eggs & Dairy")
    image_url: str = Field(..., description="The product's image URL.",
                           example="https://allthatsinteresting.com/wordpress/wp-content/uploads/2012/06/iconic-photos-1950-einstein.jpg")
    description: str = Field(..., description="The product's description.",
                             example="Local eggs. A great source of protein!!!!!!")
    price: float = Field(..., description="The product's price.", example=2.99)

    category: Optional[CategoryOut] = Field(
        None, description="The an object describing the product's category.")

class ProductUpdate(BaseModel):
    quantity: int = Field(...,
                          description="The amount of stock in our inventory.", example=100)
    price: float = Field(..., description="The product's price.", example=2.99)


