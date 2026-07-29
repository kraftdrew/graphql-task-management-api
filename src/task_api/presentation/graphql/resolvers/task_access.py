"""Shared authentication and project-access checks for task resolvers."""

from uuid import UUID

from task_api.enums import ProjectRole
from task_api.infrastructure.database.models import TaskModel, UserModel
from task_api.infrastructure.database.repositories import (
    ProjectRepository,
)
from task_api.presentation.graphql.context import GraphQLContext
from task_api.presentation.graphql.errors import (
    ForbiddenError,
    InvalidAssigneeError,
    TaskNotFoundError,
    UnauthenticatedError,
    UnauthenticatedReason,
)


async def authenticated_user_id(context: GraphQLContext) -> UUID:
    """Resolve the active user represented by the request header.

    Args:
        context: Request context containing the parsed user ID and session.

    Returns:
        UUID of the active authenticated user.

    Raises:
        UnauthenticatedError: If the header is absent, malformed, unknown, or inactive.
    """

    if context.current_user_id is None:
        raise UnauthenticatedError(UnauthenticatedReason.MISSING_CREDENTIALS)

    user = await context.session.get(UserModel, context.current_user_id)
    if user is None or not user.is_active:
        raise UnauthenticatedError(UnauthenticatedReason.UNKNOWN_OR_INACTIVE_USER)
    return user.id


async def require_project_member(
    context: GraphQLContext, project_id: UUID, user_id: UUID
) -> ProjectRole:
    """Require a user to belong to a project.

    Args:
        context: Request context containing the database session.
        project_id: Project the user must be able to access.
        user_id: User whose membership should be checked.

    Returns:
        The user's project role.

    Raises:
        ForbiddenError: If the user is not a project member.
    """

    role = await ProjectRepository(context.session).membership_role(project_id, user_id)
    if role is None:
        raise ForbiddenError
    return role


async def editable_task(context: GraphQLContext, task_id: UUID) -> tuple[UUID, TaskModel]:
    """Load a task and verify that the request user can access its project.

    Args:
        context: Request context containing identity and persistence dependencies.
        task_id: Task to load.

    Returns:
        Pair containing the authenticated user ID and visible task.

    Raises:
        UnauthenticatedError: If the request user is not authenticated and active.
        TaskNotFoundError: If the task does not exist.
        ForbiddenError: If the request user is not a member of the task's project.
    """

    actor_id = await authenticated_user_id(context)
    task = await context.session.get(TaskModel, task_id)
    if task is None:
        raise TaskNotFoundError
    await require_project_member(context, task.project_id, actor_id)
    return actor_id, task


async def require_valid_assignee(
    context: GraphQLContext, project_id: UUID, assignee_id: UUID
) -> None:
    """Validate that a user can be assigned to a project task.

    Args:
        context: Request context containing the database session.
        project_id: Project that owns the task.
        assignee_id: User proposed as the task assignee.

    Raises:
        InvalidAssigneeError: If the user is inactive, missing, or not a project member.
    """

    user = await context.session.get(UserModel, assignee_id)
    role = await ProjectRepository(context.session).membership_role(project_id, assignee_id)
    if user is None or not user.is_active or role is None:
        raise InvalidAssigneeError
