from app.database import Base
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class Address(Base):
    __tablename__ = "Address"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("User.id"))
    line1 = Column(String)
    line2 = Column(String)
    city = Column(String)
    zip_code = Column(String)
    country_code = Column(String)
