import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base

from .helpers.enums import IntEnum


class OrderStatus(enum.IntEnum):
    CART = 0
    ORDERED = 1
    OUT_FOR_DELIVERY = 2
    SHIPPED = 3


class Order(Base):
    __tablename__ = "Order"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("User.id"), nullable=False)
    status = Column(IntEnum(OrderStatus), default=OrderStatus.CART)

    stripe_id = Column(String, default="")
    updated_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    delivery = relationship("Delivery", uselist=False, back_populates="order")
    items = relationship("OrderItem", lazy="joined")
