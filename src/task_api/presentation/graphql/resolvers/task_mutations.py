"""Task mutation resolvers."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

import strawberry
from pydantic import ValidationError
from strawberry.types import Info

from task_api.enums import ProjectRole, TaskStatus
from task_api.infrastructure.database.models import ProjectModel, TaskModel
from task_api.infrastructure.database.repositories import (
    ProjectRepository,
    TaskRepository,
)
from task_api.presentation.graphql.context import GraphQLContext
from task_api.presentation.graphql.errors import (
    ForbiddenError,
    InvalidStatusTransitionError,
    ProjectNotFoundError,
    TaskNotFoundError,
    from_validation_error,
    invalid_id,
)
from task_api.presentation.graphql.resolvers.task_access import (
    authenticated_user_id,
    editable_task,
    require_project_member,
    require_valid_assignee,
)
from task_api.presentation.graphql.types.inputs import (
    CreateTaskData,
    CreateTaskInput,
    UpdateTaskInput,
)
from task_api.presentation.graphql.types.outputs import (
    DeleteTaskSuccess,
    TaskType,
)

ALLOWED_STATUS_TRANSITIONS = {
    TaskStatus.TODO: {TaskStatus.IN_PROGRESS, TaskStatus.BLOCKED},
    TaskStatus.IN_PROGRESS: {
        TaskStatus.TODO,
        TaskStatus.BLOCKED,
        TaskStatus.DONE,
    },
    TaskStatus.BLOCKED: {TaskStatus.TODO, TaskStatus.IN_PROGRESS},
    TaskStatus.DONE: {TaskStatus.IN_PROGRESS},
}


def parse_id(value: strawberry.ID, field: str = "id") -> UUID:
    """Parse an opaque GraphQL ID as a UUID.

    Args:
        value: GraphQL ID supplied by the client.
        field: Input field name used when reporting validation failure.

    Returns:
        Parsed UUID.

    Raises:
        InputValidationError: If the supplied ID is not a UUID.
    """

    try:
        return UUID(str(value))
    except ValueError as error:
        raise invalid_id(field) from error


async def resolve_create_task(
    info: Info[GraphQLContext, None],
    input: CreateTaskInput,
) -> TaskType:
    """Create a task after validating project access and assignment.

    Args:
        info: Strawberry resolver information containing the request context.
        input: Client-supplied task creation values.

    Returns:
        Created task.

    Raises:
        TaskError: If validation, authentication, or authorization fails.
    """

    try:
        data = CreateTaskData.model_validate(input, from_attributes=True)
    except ValidationError as error:
        raise from_validation_error(error) from error

    actor_id = await authenticated_user_id(info.context)
    project = await info.context.session.get(ProjectModel, data.project_id)
    if project is None:
        raise ProjectNotFoundError
    await require_project_member(info.context, data.project_id, actor_id)
    if data.assignee_id is not None:
        await require_valid_assignee(info.context, data.project_id, data.assignee_id)

    now = datetime.now(UTC)
    task = TaskModel(
        id=uuid4(),
        project_id=data.project_id,
        title=data.title,
        description=data.description,
        status=TaskStatus.TODO,
        priority=data.priority,
        assignee_id=data.assignee_id,
        created_by_id=actor_id,
        updated_by_id=actor_id,
        due_at=data.due_at,
        created_at=now,
        updated_at=now,
    )
    created = await TaskRepository(info.context.session).add(task)
    await info.context.session.commit()
    return TaskType.from_model(created)


async def resolve_update_task(
    info: Info[GraphQLContext, None],
    id: strawberry.ID,
    input: UpdateTaskInput,
) -> TaskType:
    """Apply validated partial changes to a visible task.

    Args:
        info: Strawberry resolver information containing the request context.
        id: Opaque GraphQL task ID.
        input: Client-supplied partial task changes.

    Returns:
        Updated task.

    Raises:
        TaskError: If validation, authentication, authorization, or lookup fails.
    """

    parsed_id = parse_id(id)

    try:
        data = input.to_data()
    except ValidationError as error:
        raise from_validation_error(error) from error

    actor_id, _ = await editable_task(info.context, parsed_id)
    updated = await TaskRepository(info.context.session).update_fields(
        parsed_id,
        data.changes(),
        updated_by_id=actor_id,
    )
    if updated is None:
        raise TaskNotFoundError
    await info.context.session.commit()
    return TaskType.from_model(updated)


async def resolve_change_task_status(
    info: Info[GraphQLContext, None],
    id: strawberry.ID,
    status: TaskStatus,
) -> TaskType:
    """Validate and apply a task workflow transition.

    Args:
        info: Strawberry resolver information containing the request context.
        id: Opaque GraphQL task ID.
        status: Requested workflow status.

    Returns:
        Updated task.

    Raises:
        TaskError: If validation, access, lookup, or transition validation fails.
    """

    parsed_id = parse_id(id)
    actor_id, task = await editable_task(info.context, parsed_id)
    if status == task.status:
        return TaskType.from_model(task)
    if status not in ALLOWED_STATUS_TRANSITIONS[task.status]:
        raise InvalidStatusTransitionError(task.status, status)

    repository = TaskRepository(info.context.session)
    updated = await repository.change_status(
        parsed_id,
        status=status,
        updated_by_id=actor_id,
    )
    if updated is None:
        raise TaskNotFoundError
    await info.context.session.commit()
    return TaskType.from_model(updated)


async def resolve_set_task_assignee(
    info: Info[GraphQLContext, None],
    id: strawberry.ID,
    assignee_id: strawberry.ID | None,
) -> TaskType:
    """Assign or unassign a visible task.

    Args:
        info: Strawberry resolver information containing the request context.
        id: Opaque GraphQL task ID.
        assignee_id: Opaque user ID, or ``None`` to remove the assignee.

    Returns:
        Updated task.

    Raises:
        TaskError: If validation, access, lookup, or assignee validation fails.
    """

    parsed_id = parse_id(id)

    parsed_assignee_id: UUID | None = None
    if assignee_id is not None:
        parsed_assignee_id = parse_id(assignee_id, "assigneeId")

    actor_id, task = await editable_task(info.context, parsed_id)
    if parsed_assignee_id is not None:
        await require_valid_assignee(info.context, task.project_id, parsed_assignee_id)
    updated = await TaskRepository(info.context.session).update_fields(
        parsed_id,
        {"assignee_id": parsed_assignee_id},
        updated_by_id=actor_id,
    )
    if updated is None:
        raise TaskNotFoundError
    await info.context.session.commit()
    return TaskType.from_model(updated)


async def resolve_delete_task(
    info: Info[GraphQLContext, None], id: strawberry.ID
) -> DeleteTaskSuccess:
    """Delete a task when the request user owns its project.

    Args:
        info: Strawberry resolver information containing the request context.
        id: Opaque GraphQL task ID.

    Returns:
        Deletion confirmation.

    Raises:
        TaskError: If validation, access, or lookup fails.
    """

    parsed_id = parse_id(id)
    actor_id, task = await editable_task(info.context, parsed_id)
    role = await ProjectRepository(info.context.session).membership_role(task.project_id, actor_id)
    if role is not ProjectRole.OWNER:
        raise ForbiddenError
    if not await TaskRepository(info.context.session).delete(parsed_id):
        raise TaskNotFoundError
    await info.context.session.commit()
    return DeleteTaskSuccess(deleted_task_id=id)
