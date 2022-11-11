
import asyncio
from typing import AsyncGenerator, Callable

import pytest
from fastapi import HTTPException
from httpx import AsyncClient
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app import app
from app.database import get_database
from app.models import create_all_tables
from manage.database import populate_database

ASYNC_DATABASE_URL = 'postgresql+asyncpg://producegoose:drowssap@localhost:5432/test'

pytestmark = pytest.mark.asyncio

engine = create_async_engine(ASYNC_DATABASE_URL)
async_session_factory: Callable[[], AsyncSession] = sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession
)

async def get_database_monkeypath() -> AsyncGenerator:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except SQLAlchemyError as sql_ex:
            await session.rollback()
            raise sql_ex
        except HTTPException as http_ex:
            await session.rollback()
            raise http_ex
        finally:
            await session.close()

app.dependency_overrides[get_database] = get_database_monkeypath


@pytest.fixture(scope='session')
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope='session', autouse=True)
async def database():
    await create_all_tables(drop_all=True, engine=engine)
    await populate_database(async_session_factory)
    
    

@pytest.fixture()
async def client():
    async with AsyncClient(app=app, base_url='http://test') as ac:
        yield ac
