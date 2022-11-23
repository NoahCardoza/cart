from typing import ForwardRef, List, Optional

from pydantic import BaseModel, Field, conint

from .orm import OrmBaseModel

# if TYPE_CHECKING:
    # from .category import CategoryOut

CategoryOut = ForwardRef('CategoryOut')

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



# stooopid circular deps

class CategoryIn(OrmBaseModel):
    parent_id: Optional[int] = Field(
        None, description="The ID of the parent category.", example=42)
    image_url: str = Field(..., description="The URL of the category image.",
                           example="https://allthatsinteresting.com/wordpress/wp-content/uploads/2012/06/iconic-photos-1950-einstein.jpg")
    name: str = Field(..., description="The name of the category.",
                      example="Eggs & Dairy")
    description: str = Field(..., description="The description of the category.",
                             example="Our eggs and dairy products are locally source and delivered rotten!")

class CategoryOut(CategoryIn):
    id: int = Field(..., description="The ID of the category.", example=420)
    slug: str = Field(..., description="The slug of the category.",
                      example="eggs-dairy")
    products: Optional[List['ProductOut']] = Field(None, description="The products of this category if expanded.")


ProductOut.update_forward_refs()