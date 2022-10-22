from app.database import Base
from sqlalchemy import Column, Float, ForeignKey, Integer, String, event
from sqlalchemy.orm import relationship

from .helpers import slugify_listener


class Product(Base):
    __tablename__ = "Product"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, index=True)
    category_id = Column(Integer, ForeignKey("Category.id"))
    category = relationship("Category", back_populates="products")
    quantity = Column(Integer, default=0)
    name = Column(String)
    image_url = Column(String)
    description = Column(String)
    price = Column(Float)


event.listen(Product.name, 'set', slugify_listener, retval=False)
