"""Integration test proving Alembic creates the expected PostgreSQL schema."""

from sqlalchemy import inspect
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine


def table_names(connection: Connection) -> set[str]:
    """Return public table names visible through a synchronous connection.

    Args:
        connection: SQLAlchemy connection bridged from the async engine.

    Returns:
        Names of tables created in the test database.
    """

    return set(inspect(connection).get_table_names())


async def test_migrations_create_required_tables(test_engine: AsyncEngine) -> None:
    """Verify that Alembic creates every table required by the application."""

    async with test_engine.connect() as connection:
        tables = await connection.run_sync(table_names)

    assert {"alembic_version", "users", "projects", "project_members", "tasks"} <= tables
