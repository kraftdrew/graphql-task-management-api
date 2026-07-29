"""Database, application, and seed fixtures shared by the test suite."""

import os
from collections.abc import AsyncIterator, Iterator

import httpx
import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://task_api_test:task_api_test@localhost:55432/task_api_test",
)
test_database_name = make_url(TEST_DATABASE_URL).database
if test_database_name is None or not test_database_name.endswith("_test"):
    raise RuntimeError("TEST_DATABASE_URL must reference a database ending in '_test'.")

# Application modules read DATABASE_URL during import.
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

from task_api.infrastructure.database.session import get_session  # noqa: E402
from task_api.main import app  # noqa: E402
from tests.support import SeedData, create_seed_data  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def migrated_database() -> Iterator[None]:
    """Apply all migrations to the dedicated test database once per test run.

    Yields:
        Control after the test schema reaches the latest migration.
    """

    command.upgrade(Config("alembic.ini"), "head")
    yield


@pytest_asyncio.fixture(scope="session")
async def test_engine(migrated_database: None) -> AsyncIterator[AsyncEngine]:
    """Create the asynchronous engine shared by rollback-isolated tests.

    Args:
        migrated_database: Completed migration setup.

    Yields:
        Engine connected only to the dedicated test database.
    """

    engine = create_async_engine(TEST_DATABASE_URL, pool_pre_ping=True)
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
    """Provide a session whose commits remain inside an outer transaction.

    Args:
        test_engine: Engine connected to the migrated test database.

    Yields:
        Session used by the test and application dependency override.
    """

    async with test_engine.connect() as connection:
        # The connection owns the real transaction so application sessions
        # cannot permanently commit test data.
        outer_transaction = await connection.begin()
        session = AsyncSession(
            bind=connection,
            expire_on_commit=False,
            autoflush=False,
            # Resolver commit/rollback calls operate on savepoints while the
            # connection-level transaction remains under fixture control.
            join_transaction_mode="create_savepoint",
        )
        try:
            yield session
        finally:
            await session.close()
            if outer_transaction.is_active:
                await outer_transaction.rollback()


@pytest_asyncio.fixture
async def api_client(db_session: AsyncSession) -> AsyncIterator[httpx.AsyncClient]:
    """Call the FastAPI application while reusing the isolated test session.

    Args:
        db_session: Rollback-isolated session supplied to GraphQL context creation.

    Yields:
        HTTP client executing requests directly against the ASGI application.
    """

    async def override_get_session() -> AsyncIterator[AsyncSession]:
        """Yield the same rollback-isolated session to the request context."""

        yield db_session

    # In-process HTTP requests must use the fixture session; otherwise the
    # application engine would open a separate, non-rollback-isolated connection.
    app.dependency_overrides[get_session] = override_get_session
    transport = httpx.ASGITransport(app=app)
    try:
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://test",
        ) as client:
            yield client
    finally:
        app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def seed_data(db_session: AsyncSession) -> SeedData:
    """Insert the standard related test dataset.

    Args:
        db_session: Rollback-isolated session receiving the models.

    Returns:
        Persisted test models.
    """

    return await create_seed_data(db_session)
