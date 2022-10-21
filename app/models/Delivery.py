from datetime import datetime

from app.database import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship


class Delivery(Base):
    __tablename__ = "Delivery"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("Order.id"))
    address_id = Column(Integer, ForeignKey("Address.id"))
    expected_delivery_at = Column(DateTime, default=datetime.utcnow)
    arrived_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order", uselist=False, back_populates="delivery")
