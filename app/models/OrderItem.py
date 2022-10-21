from app.database import Base
from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship


class OrderItem(Base):
    __tablename__ = "OrderItem"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("Order.id"))
    product_id = Column(Integer, ForeignKey("Product.id"))
    quantity = Column(Integer)
