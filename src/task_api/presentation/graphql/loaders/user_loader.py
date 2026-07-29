"""Create the user DataLoader stored in each GraphQL request context.

Task field resolvers use this loader for assignee, creator, and updater fields.
The shared generic loader owns the batching, caching, ordering, and session-lock
behavior.
"""

from asyncio import Lock
from uuid import UUID

from strawberry.dataloader import DataLoader

from task_api.infrastructure.database.models import UserModel
from task_api.infrastructure.database.repositories import UserRepository
from task_api.presentation.graphql.loaders.generic_loader import create_loader


def create_user_loader(
    repository: UserRepository,
    session_lock: Lock,
) -> DataLoader[UUID, UserModel | None]:
    """Configure a UUID DataLoader for ``UserModel`` objects.

    Args:
        repository: User repository used for batched primary-key reads.
        session_lock: Request-scoped lock protecting the shared SQLAlchemy
            session.

    Returns:
        A loader whose ``load(user_id)`` call returns the matching user or
        ``None``.

    Example:
        The loader is created in the GraphQL context and consumed by a field
        resolver:

        >>> user_loader = create_user_loader(UserRepository(session), session_lock)
        >>> user = await user_loader.load(task.created_by_id)
    """

    return create_loader(repository.get_many, lambda user: user.id, session_lock)
