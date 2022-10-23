from os import environ
from typing import AsyncGenerator, Callable

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app import environ

# heroku will use the plain posrgres:// url
# but we're using asyncpg so we need to use postgresql+asyncpg://
ASYNC_DATABASE_URL = environ.DATABASE_URL.replace(
    "postgres://",
    "postgresql+asyncpg://"
).replace(
    "postgresql://",
    "postgresql+asyncpg://"
)

engine = create_async_engine(
    ASYNC_DATABASE_URL,
    # only show the sql quries in development
    echo=environ.DEVELOPMENT
)

# expire_on_commit=False will prevent attributes from being expired
# after commit.
async_session_factory: Callable[[], AsyncSession] = sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession
)

Base = declarative_base()


async def get_database() -> AsyncGenerator:
    """Get a database session.

    Automatically rolls back the session if an exception is raised.

    Raises:
        SQLAlchemyError: An error occured while talking to the database.
        HTTPException: An general HTTP error occured.

    Returns:
        AsyncGenerator: A generator that yields a database session to a route.

    Yields:
        Iterator[AsyncGenerator]: A session to the database.
    """
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
