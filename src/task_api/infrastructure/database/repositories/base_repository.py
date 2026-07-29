"""Generic asynchronous persistence operations for UUID-keyed models."""

from collections.abc import Mapping, Sequence
from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy import delete, inspect, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement

from task_api.infrastructure.database.models import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Provide shared CRUD operations for a single-primary-key model."""

    def __init__(self, session: AsyncSession, model: type[ModelT]) -> None:
        """Bind persistence operations to a session and mapped model.

        Args:
            session: Request-scoped SQLAlchemy session.
            model: Mapped model handled by this repository.

        Raises:
            ValueError: If the model does not have exactly one primary-key column.
        """

        self.session = session
        self.model = model

        # Generic update, delete, and batch reads need the mapped primary-key
        # expression. Mapper inspection avoids repeating it in every repository.
        primary_key = inspect(model).primary_key
        if len(primary_key) != 1:
            raise ValueError(f"{model.__name__} must have exactly one primary-key column.")
        self._primary_key: ColumnElement[Any] = primary_key[0]

    async def add(self, model: ModelT) -> ModelT:
        """Stage and flush a model without committing the transaction.

        Args:
            model: New mapped instance to persist.

        Returns:
            The flushed model, including database-generated values.
        """

        self.session.add(model)
        await self.session.flush()
        return model

    async def get_many(self, model_ids: Sequence[UUID]) -> list[ModelT]:
        """Fetch models by a collection of primary-key values.

        Args:
            model_ids: UUID primary keys to fetch.

        Returns:
            Matching models in database result order. Missing IDs are omitted.
        """

        if not model_ids:
            return []

        return list(
            (
                await self.session.scalars(
                    select(self.model).where(self._primary_key.in_(model_ids))
                )
            ).all()
        )

    async def update(self, model_id: UUID, values: Mapping[str, Any]) -> ModelT | None:
        """Apply last-write-wins changes to one model.

        Args:
            model_id: UUID primary key of the row to update.
            values: Mapped column names and replacement values.

        Returns:
            The updated model, or ``None`` when the row does not exist.
        """

        result = await self.session.execute(
            update(self.model)
            .where(self._primary_key == model_id)
            .values(**values)
            .returning(self.model)
        )
        return result.scalar_one_or_none()

    async def delete(self, model_id: UUID) -> bool:
        """Delete one model by primary key.

        Args:
            model_id: UUID primary key of the row to delete.

        Returns:
            ``True`` when a row was deleted; otherwise ``False``.
        """

        deleted_id = await self.session.scalar(
            delete(self.model).where(self._primary_key == model_id).returning(self._primary_key)
        )
        return deleted_id is not None
