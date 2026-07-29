"""Root GraphQL mutation declaration."""

import strawberry

from task_api.presentation.graphql.resolvers.task_mutations import (
    resolve_change_task_status,
    resolve_create_task,
    resolve_delete_task,
    resolve_set_task_assignee,
    resolve_update_task,
)
from task_api.presentation.graphql.types.outputs import DeleteTaskSuccess, TaskType


@strawberry.type(description="Write operations available in the task API.")
class Mutation:
    """Task mutation fields exposed by the GraphQL API."""

    create_task: TaskType = strawberry.mutation(
        resolver=resolve_create_task,
        description="Create a task in a project where the authenticated user is a member.",
    )
    update_task: TaskType = strawberry.mutation(
        resolver=resolve_update_task,
        description="Update editable fields of an existing task.",
    )
    change_task_status: TaskType = strawberry.mutation(
        resolver=resolve_change_task_status,
        description="Move a task to another allowed workflow status.",
    )
    set_task_assignee: TaskType = strawberry.mutation(
        resolver=resolve_set_task_assignee,
        description="Assign an eligible project member to a task or remove its assignee.",
    )
    delete_task: DeleteTaskSuccess = strawberry.mutation(
        resolver=resolve_delete_task,
        description="Permanently delete a task.",
    )
