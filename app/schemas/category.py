from typing import Optional

from pydantic import Field

from .orm import OrmBaseModel


class CategoryOut(OrmBaseModel):
    id: int = Field(..., description="The ID of the category.", example=420)
    parent_id: Optional[int] = Field(
        None, description="The ID of the parent category.", example=42)

    slug: str = Field(..., description="The slug of the category.",
                      example="eggs-dairy")
    image_url: str = Field(..., description="The URL of the category image.",
                           example="https://allthatsinteresting.com/wordpress/wp-content/uploads/2012/06/iconic-photos-1950-einstein.jpg")
    name: str = Field(..., description="The name of the category.",
                      example="Eggs & Dairy")
    description: str = Field(..., description="The description of the category.",
                             example="Our eggs and dairy products are locally source and delivered fresh!")
