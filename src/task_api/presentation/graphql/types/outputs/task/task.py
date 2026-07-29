"""GraphQL task type and relationship resolvers."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

import strawberry
from strawberry.types import Info

from task_api.enums import TaskPriority, TaskStatus
from task_api.infrastructure.database.models import TaskModel
from task_api.presentation.graphql.context import GraphQLContext
from task_api.presentation.graphql.types.outputs.project.project import ProjectType
from task_api.presentation.graphql.types.outputs.user.user import UserType


@strawberry.type(
    name="Task",
    description="A task managed inside a project.",
)
class TaskType:
    """Public GraphQL representation of a task and its relationships."""

    id: strawberry.ID = strawberry.field(description="Unique task identifier.")
    title: str = strawberry.field(description="Short title describing the task.")
    description: str | None = strawberry.field(
        description="Optional detailed description of the task."
    )
    status: TaskStatus = strawberry.field(description="Current workflow status.")
    priority: TaskPriority = strawberry.field(description="Current task priority.")
    due_at: datetime | None = strawberry.field(
        description="Optional deadline for completing the task."
    )
    created_at: datetime = strawberry.field(description="Date and time when the task was created.")
    updated_at: datetime = strawberry.field(
        description="Date and time when the task was last changed."
    )

    # Hidden foreign keys support nested resolution without entering the public schema.
    project_id: strawberry.Private[UUID]
    assignee_id: strawberry.Private[UUID | None]
    created_by_id: strawberry.Private[UUID]
    updated_by_id: strawberry.Private[UUID]

    @classmethod
    def from_model(cls, task: TaskModel) -> TaskType:
        """Create a GraphQL task from a database model.

        Args:
            task: Persisted task model.

        Returns:
            Public GraphQL task representation with private relationship IDs.
        """

        return cls(
            id=strawberry.ID(str(task.id)),
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            due_at=task.due_at,
            created_at=task.created_at,
            updated_at=task.updated_at,
            project_id=task.project_id,
            assignee_id=task.assignee_id,
            created_by_id=task.created_by_id,
            updated_by_id=task.updated_by_id,
        )

    @strawberry.field(  # type: ignore[untyped-decorator]
        description="Project that owns the task."
    )
    async def project(self, info: Info[GraphQLContext, None]) -> ProjectType:
        """Resolve the task's project.

        Args:
            info: Strawberry resolver information containing request DataLoaders.

        Returns:
            Project that owns this task.

        Raises:
            RuntimeError: If the task references a missing project.
        """

        project = await info.context.project_loader.load(self.project_id)
        if project is None:
            raise RuntimeError("Task references a missing project.")
        return ProjectType.from_model(project)

    @strawberry.field(  # type: ignore[untyped-decorator]
        description="User assigned to the task, if any."
    )
    async def assignee(self, info: Info[GraphQLContext, None]) -> UserType | None:
        """Resolve the optional task assignee.

        Args:
            info: Strawberry resolver information containing request DataLoaders.

        Returns:
            Assigned user, or ``None`` for an unassigned or missing user.
        """

        if self.assignee_id is None:
            return None
        user = await info.context.user_loader.load(self.assignee_id)
        return UserType.from_model(user) if user else None

    @strawberry.field(  # type: ignore[untyped-decorator]
        description="User who created the task."
    )
    async def created_by(self, info: Info[GraphQLContext, None]) -> UserType:
        """Resolve the user who created the task.

        Args:
            info: Strawberry resolver information containing request DataLoaders.

        Returns:
            User who created this task.

        Raises:
            RuntimeError: If the task references a missing creator.
        """

        user = await info.context.user_loader.load(self.created_by_id)
        if user is None:
            raise RuntimeError("Task references a missing creator.")
        return UserType.from_model(user)

    @strawberry.field(  # type: ignore[untyped-decorator]
        description="User who most recently changed the task."
    )
    async def updated_by(self, info: Info[GraphQLContext, None]) -> UserType:
        """Resolve the user who last updated the task.

        Args:
            info: Strawberry resolver information containing request DataLoaders.

        Returns:
            User who last updated this task.

        Raises:
            RuntimeError: If the task references a missing editor.
        """

        user = await info.context.user_loader.load(self.updated_by_id)
        if user is None:
            raise RuntimeError("Task references a missing editor.")
        return UserType.from_model(user)
