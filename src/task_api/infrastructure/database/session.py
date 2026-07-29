"""Asynchronous database engine and request-session factory."""

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from task_api.config import get_settings

settings = get_settings()
engine: AsyncEngine = create_async_engine(settings.database_url, pool_pre_ping=True)
session_factory = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    """Provide one database session per request.

    Yields:
        Session shared by resolvers executed for the current request.
    """

    async with session_factory() as session:
        try:
            yield session
        finally:
            # Read-only requests may still autobegin a transaction. Roll it
            # back before returning the connection to the pool.
            if session.in_transaction():
                await session.rollback()
