from app.database import Base
from sqlalchemy import Column, ForeignKey, Integer, String, event
from sqlalchemy.orm import relationship

from .helpers import slugify_listener


class Category(Base):
    __tablename__ = "Category"
    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("Category.id"))

    slug = Column(String, unique=True, index=True, nullable=False)
    image_url = Column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)

    children = relationship('Category', remote_side='Category.parent_id')
    products = relationship('Product', back_populates='category')


event.listen(Category.name, 'set', slugify_listener, retval=False)
