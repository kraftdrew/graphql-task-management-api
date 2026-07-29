"""Root GraphQL query declaration."""

import strawberry

from task_api.presentation.graphql.resolvers.task_queries import (
    resolve_task,
    resolve_tasks,
)
from task_api.presentation.graphql.types.outputs import TaskPageType, TaskType


@strawberry.type(description="Read operations available in the task API.")
class Query:
    """Task query fields exposed by the GraphQL API."""

    task: TaskType = strawberry.field(
        resolver=resolve_task,
        description="Return one task visible to the authenticated user.",
    )
    tasks: TaskPageType = strawberry.field(
        resolver=resolve_tasks,
        description="Return a filtered, sorted, and paginated list of visible tasks.",
    )
