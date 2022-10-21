from app.database import Base
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class Category(Base):
    __tablename__ = "Category"
    id = Column(Integer, primary_key=True, index=True)
    image = Column(String)
    name = Column(String)
    description = Column(String)

    parent_id = Column(Integer, ForeignKey("Category.id"))
    children = relationship('Category', remote_side='Category.parent_id')
    products = relationship('Product', back_populates='category')
