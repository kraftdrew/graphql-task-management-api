"""Paginated GraphQL task output type."""

from __future__ import annotations

import strawberry

from task_api.infrastructure.database.models import TaskModel
from task_api.presentation.graphql.types.outputs.task.task import TaskType


@strawberry.type(
    name="TaskPage",
    description="One page of tasks with offset-pagination metadata.",
)
class TaskPageType:
    """GraphQL task page with offset-pagination metadata."""

    items: list[TaskType] = strawberry.field(description="Tasks contained in this page.")
    total: int = strawberry.field(description="Total tasks matching the query.")
    page: int = strawberry.field(description="Current one-based page number.")
    pages: int = strawberry.field(description="Total number of available pages.")
    per_page: int = strawberry.field(description="Maximum number of tasks requested per page.")
    next_page: int | None = strawberry.field(
        description="Next page number, or null on the final page."
    )
    prev_page: int | None = strawberry.field(
        description="Previous page number, or null on the first page."
    )
    last_page: int = strawberry.field(description="Final available page number.")

    @classmethod
    def from_models(
        cls,
        models: list[TaskModel],
        *,
        total: int,
        page: int,
        per_page: int,
    ) -> TaskPageType:
        """Create a GraphQL page and calculate navigation metadata.

        Args:
            models: Task models returned for the current page.
            total: Total tasks matching the query before pagination.
            page: Current one-based page number.
            per_page: Requested maximum tasks per page.

        Returns:
            GraphQL task page with total, page count, and navigation fields.
        """

        pages = (total + per_page - 1) // per_page
        return cls(
            items=[TaskType.from_model(task) for task in models],
            total=total,
            page=page,
            pages=pages,
            per_page=per_page,
            next_page=page + 1 if page < pages else None,
            prev_page=page - 1 if page > 1 else None,
            last_page=pages,
        )
