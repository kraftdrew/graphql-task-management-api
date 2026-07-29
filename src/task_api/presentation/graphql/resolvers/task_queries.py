"""Task query resolvers."""

from uuid import UUID

import strawberry
from pydantic import ValidationError
from strawberry.types import Info

from task_api.infrastructure.database.models import ProjectModel, TaskModel
from task_api.infrastructure.database.repositories import TaskRepository
from task_api.presentation.graphql.context import GraphQLContext
from task_api.presentation.graphql.errors import (
    ProjectNotFoundError,
    TaskNotFoundError,
    from_validation_error,
    invalid_id,
)
from task_api.presentation.graphql.resolvers.task_access import (
    authenticated_user_id,
    require_project_member,
)
from task_api.presentation.graphql.types.inputs import (
    TaskFilterData,
    TaskFilterInput,
    TaskSortData,
    TaskSortInput,
    page_data,
)
from task_api.presentation.graphql.types.outputs import (
    TaskPageType,
    TaskType,
)


async def resolve_task(info: Info[GraphQLContext, None], id: strawberry.ID) -> TaskType:
    """Resolve one task visible to the request user.

    Args:
        info: Strawberry resolver information containing the request context.
        id: Opaque GraphQL task ID.

    Returns:
        Visible task.

    Raises:
        TaskError: If validation, authentication, access, or lookup fails.
    """

    try:
        task_id = UUID(str(id))
    except ValueError as error:
        raise invalid_id("id") from error

    actor_id = await authenticated_user_id(info.context)
    task = await info.context.session.get(TaskModel, task_id)
    if task is None:
        raise TaskNotFoundError
    await require_project_member(info.context, task.project_id, actor_id)
    return TaskType.from_model(task)


async def resolve_tasks(
    info: Info[GraphQLContext, None],
    filter: TaskFilterInput | None = None,
    sort: TaskSortInput | None = None,
    page: int = 1,
    per_page: int = 24,
) -> TaskPageType:
    """Resolve a filtered and sorted page of visible tasks.

    Args:
        info: Strawberry resolver information containing the request context.
        filter: Optional task filters.
        sort: Optional task sort field and direction.
        page: One-based page number.
        per_page: Maximum tasks returned per page.

    Returns:
        Task page with navigation metadata.

    Raises:
        TaskError: If validation, authentication, or project access fails.
    """

    try:
        filters = filter.to_data() if filter else TaskFilterData()
        sorting = sort.to_data() if sort else TaskSortData()
        pagination = page_data(page, per_page)
    except ValidationError as error:
        raise from_validation_error(error) from error

    actor_id = await authenticated_user_id(info.context)

    if filters.project_id is not None:
        project = await info.context.session.get(ProjectModel, filters.project_id)
        if project is None:
            raise ProjectNotFoundError
        await require_project_member(info.context, filters.project_id, actor_id)

    items, total = await TaskRepository(info.context.session).list_page(
        user_id=actor_id,
        filters=filters.query_values(),
        sort_field=sorting.field,
        direction=sorting.direction,
        limit=pagination.per_page,
        offset=(pagination.page - 1) * pagination.per_page,
    )
    return TaskPageType.from_models(
        items,
        total=total,
        page=pagination.page,
        per_page=pagination.per_page,
    )
