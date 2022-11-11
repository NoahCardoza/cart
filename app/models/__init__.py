from app.database import Base
from app.database import engine as _engine

# import all models so that they are registered with the metadata
from .Address import Address
from .Category import Category
from .Delivery import Delivery
from .Order import Order, OrderStatus
from .OrderItem import OrderItem
from .Product import Product
from .User import User


async def create_all_tables(drop_all=False, engine=_engine):
    """Drops all tables and then recreates them"""
    async with engine.begin() as conn:
        if drop_all:
            await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
