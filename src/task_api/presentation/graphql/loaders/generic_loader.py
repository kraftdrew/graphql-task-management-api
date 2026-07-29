"""Build request-scoped DataLoaders for UUID-keyed database models.

Strawberry resolvers call ``loader.load(model_id)`` independently. The DataLoader
collects calls made during the same event-loop turn and invokes one ``load_many``
query for all collected IDs. It also caches each result for the lifetime of the
loader, which is one GraphQL request in this application.

The batch callback restores the requested key order because a SQL ``IN`` query
does not preserve it. It also inserts ``None`` for IDs that were not found, as
required by the DataLoader contract.

Example:
    Create a loader once while building the request context, then reuse it from
    field resolvers:

    >>> loader = create_loader(
    ...     repository.get_many,
    ...     lambda user: user.id,
    ...     session_lock,
    ... )
    >>> user = await loader.load(user_id)
"""

from asyncio import Lock
from collections.abc import Awaitable, Callable, Sequence
from typing import TypeVar
from uuid import UUID

from strawberry.dataloader import DataLoader

ModelT = TypeVar("ModelT")


def create_loader(
    load_many: Callable[[Sequence[UUID]], Awaitable[Sequence[ModelT]]],
    get_id: Callable[[ModelT], UUID],
    session_lock: Lock,
) -> DataLoader[UUID, ModelT | None]:
    """Create a batching and caching loader for one model type.

    Calls to ``load`` are grouped into a single ``load_many`` call. The returned
    models are indexed by ``get_id`` and realigned with the requested keys, so
    duplicate keys and missing database rows are handled correctly.

    The lock serializes database reads made by different loaders because they
    share the same request-scoped SQLAlchemy ``AsyncSession``. The lock does not
    prevent GraphQL resolvers from running concurrently; it only prevents their
    SQL statements from using that session at the same time.

    Args:
        load_many: Async repository method that accepts UUIDs and returns every
            matching model. Its result may be unordered and may omit missing IDs.
        get_id: Function that extracts the UUID primary key from a returned model.
        session_lock: Request-scoped lock that serializes access to the shared
            SQLAlchemy session.

    Returns:
        A DataLoader whose ``load`` method returns the matching model or ``None``.
        The loader batches and caches values for its own lifetime.

    Example:
        Given three resolver calls made during the same event-loop turn:

        >>> first = loader.load(first_id)
        >>> second = loader.load(second_id)
        >>> repeated = loader.load(first_id)
        >>> first_user, second_user, cached_user = await asyncio.gather(
        ...     first,
        ...     second,
        ...     repeated,
        ... )

        DataLoader calls ``load_many`` with the distinct IDs and reuses the first
        result for ``repeated``.
    """

    async def load_batch(keys: list[UUID]) -> list[ModelT | None]:
        """Fetch one collected batch and align its results with the input keys.

        Args:
            keys: UUIDs collected by DataLoader for the current batch.

        Returns:
            One value per key in the same order as ``keys``. A missing database
            row is represented by ``None``.
        """

        async with session_lock:
            models = await load_many(keys)
        # SQL does not guarantee the same order as an IN-list. DataLoader
        # requires one output per input key in exactly the requested order.
        by_id = {get_id(model): model for model in models}
        return [by_id.get(key) for key in keys]

    return DataLoader(load_fn=load_batch)
