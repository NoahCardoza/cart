import asyncio

from app.models import recreate_all_tables

asyncio.run(recreate_all_tables())
