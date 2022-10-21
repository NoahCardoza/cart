from app.database import Base
from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class Product(Base):
    __tablename__ = "Product"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("Category.id"))
    category = relationship("Category", back_populates="products")
    quantity = Column(Integer)
    name = Column(String)
    image = Column(String)
    description = Column(String)
    price = Column(Float)
