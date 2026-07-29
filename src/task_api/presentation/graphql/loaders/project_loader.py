"""Create the project DataLoader stored in each GraphQL request context.

Task field resolvers use this loader to resolve their related project. The
shared generic loader owns the batching, caching, ordering, and session-lock
behavior.
"""

from asyncio import Lock
from uuid import UUID

from strawberry.dataloader import DataLoader

from task_api.infrastructure.database.models import ProjectModel
from task_api.infrastructure.database.repositories import ProjectRepository
from task_api.presentation.graphql.loaders.generic_loader import create_loader


def create_project_loader(
    repository: ProjectRepository,
    session_lock: Lock,
) -> DataLoader[UUID, ProjectModel | None]:
    """Configure a UUID DataLoader for ``ProjectModel`` objects.

    Args:
        repository: Project repository used for batched primary-key reads.
        session_lock: Request-scoped lock protecting the shared SQLAlchemy
            session.

    Returns:
        A loader whose ``load(project_id)`` call returns the matching project or
        ``None``.

    Example:
        The loader is created in the GraphQL context and consumed by a field
        resolver:

        >>> project_loader = create_project_loader(
        ...     ProjectRepository(session),
        ...     session_lock,
        ... )
        >>> project = await project_loader.load(task.project_id)
    """

    return create_loader(repository.get_many, lambda project: project.id, session_lock)
