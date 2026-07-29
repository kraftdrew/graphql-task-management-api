"""Project-specific database queries."""

from typing import cast
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from task_api.enums import ProjectRole
from task_api.infrastructure.database.models import ProjectMemberModel, ProjectModel
from task_api.infrastructure.database.repositories.base_repository import BaseRepository


class ProjectRepository(BaseRepository[ProjectModel]):
    """Provide persistence and membership queries for projects."""

    def __init__(self, session: AsyncSession) -> None:
        """Bind project operations to a request-scoped session.

        Args:
            session: Session used for project queries and persistence.
        """

        super().__init__(session, ProjectModel)

    async def membership_role(self, project_id: UUID, user_id: UUID) -> ProjectRole | None:
        """Look up a user's role in a project.

        Args:
            project_id: Project whose membership should be checked.
            user_id: User whose role should be returned.

        Returns:
            The membership role, or ``None`` when the user is not a member.
        """

        return cast(
            ProjectRole | None,
            await self.session.scalar(
                select(ProjectMemberModel.role).where(
                    ProjectMemberModel.project_id == project_id,
                    ProjectMemberModel.user_id == user_id,
                )
            ),
        )
