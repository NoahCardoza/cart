from typing import Any, Optional

from pydantic import BaseModel, Field
from pydantic.utils import GetterDict
from sqlalchemy.orm.base import instance_dict

from .category import CategoryOut


class ORMNoLazyLoaderGetter(GetterDict):
    def get(self, key: str, default: Any) -> Any:
        try:
            return instance_dict(self._obj)[key]
        except KeyError:
            return default


class ProductOut(BaseModel):
    id: int = Field(..., description="The product's ID.", example=420)
    category_id: int = Field(...,
                             description="The product's category ID.", example=42)

    slug: str = Field(..., description="The product's slug.",
                      example="eggs-dairy")
    quantity: int = Field(...,
                          description="The amount of stock in our inventory.", example=100)
    name: str = Field(..., description="The product's name.",
                      example="Eggs & Dairy")
    image_url: str = Field(..., description="The product's image URL.",
                           example="https://allthatsinteresting.com/wordpress/wp-content/uploads/2012/06/iconic-photos-1950-einstein.jpg")
    description: str = Field(..., description="The product's description.",
                             example="Local eggs. A great source of protein.")
    price: float = Field(..., description="The product's price.", example=2.99)

    category: Optional[CategoryOut] = Field(
        None, description="The an object describing the product's category.")

    class Config:
        orm_mode = True
        getter_dict = ORMNoLazyLoaderGetter
