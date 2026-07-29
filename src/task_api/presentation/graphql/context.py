"""Build the request-scoped dependencies available to GraphQL resolvers."""

from asyncio import Lock
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.dataloader import DataLoader
from strawberry.fastapi import BaseContext

from task_api.infrastructure.database.models import ProjectModel, UserModel
from task_api.infrastructure.database.repositories import (
    ProjectRepository,
    UserRepository,
)
from task_api.infrastructure.database.session import get_session
from task_api.presentation.graphql.loaders import create_project_loader, create_user_loader


class GraphQLContext(BaseContext):
    """Values shared by every resolver executed for one HTTP request."""

    def __init__(
        self,
        *,
        current_user_id: UUID | None,
        session: AsyncSession,
        user_loader: DataLoader[UUID, UserModel | None],
        project_loader: DataLoader[UUID, ProjectModel | None],
    ) -> None:
        """Store dependencies shared by resolvers for one request.

        Args:
            current_user_id: Parsed stub-authentication user ID, if valid.
            session: Request-scoped SQLAlchemy session.
            user_loader: Request-scoped batched user loader.
            project_loader: Request-scoped batched project loader.
        """

        # Identity is parsed here; services still verify that the user exists and is active.
        self.current_user_id = current_user_id
        # Resolvers and repositories share this request-scoped database transaction.
        self.session = session
        # These loaders batch and cache related-entity reads only for this request.
        self.user_loader = user_loader
        self.project_loader = project_loader


# FastAPI calls this dependency once for each incoming GraphQL HTTP request.
async def get_context(
    session: Annotated[AsyncSession, Depends(get_session)],
    x_user_id: Annotated[str | None, Header(alias="X-User-ID")] = None,
) -> GraphQLContext:
    """Build resolver dependencies for one GraphQL request.

    Args:
        session: Session supplied by the FastAPI database dependency.
        x_user_id: Optional user UUID from the ``X-User-ID`` header.

    Returns:
        Context containing identity, session, and request-scoped loaders.
    """

    # Missing or malformed credentials become a top-level UNAUTHENTICATED GraphQL error.
    try:
        current_user_id = UUID(x_user_id) if x_user_id else None
    except ValueError:
        current_user_id = None

    # Different GraphQL fields resolve concurrently, but one AsyncSession cannot run
    # concurrent SQL statements. Both loaders therefore coordinate through this lock.
    session_lock = Lock()
    return GraphQLContext(
        current_user_id=current_user_id,
        session=session,
        user_loader=create_user_loader(UserRepository(session), session_lock),
        project_loader=create_project_loader(ProjectRepository(session), session_lock),
    )
