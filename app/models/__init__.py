from app.database import Base, engine

# import all models so that they are registered with the metadata
from .Address import Address
from .Category import Category
from .Delivery import Delivery
from .Order import Order
from .OrderItem import OrderItem
from .Product import Product
from .User import User


async def recreate_all_tables():
    """Drops all tables and then recreates them"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
