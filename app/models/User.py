from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "User"
    id = Column(Integer, primary_key=True, index=True)
    stripe_id = Column(String, nullable=False)
    
    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    is_superuser = Column(Boolean, default=False)
    is_employee = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    addresses = relationship("Address")
