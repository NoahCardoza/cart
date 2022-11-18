from app.database import Base
from sqlalchemy import Column, Float, ForeignKey, Integer, String, event
from sqlalchemy.orm import relationship

from .helpers import slugify_listener


class Product(Base):
    __tablename__ = "Product"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, index=True, nullable=False)
    category_id = Column(Integer, ForeignKey("Category.id"), nullable=False)
    category = relationship("Category", back_populates="products")
    quantity = Column(Integer, default=0)
    name = Column(String, nullable=False)
    image_url = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    weight = Column(Float, nullable=False)


event.listen(Product.name, 'set', slugify_listener, retval=False)
