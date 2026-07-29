"""Task-specific database queries and updates."""

from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from task_api.enums import SortDirection, TaskSortField, TaskStatus
from task_api.infrastructure.database.models import ProjectMemberModel, TaskModel
from task_api.infrastructure.database.repositories.base_repository import BaseRepository

_SORT_COLUMNS: dict[TaskSortField, InstrumentedAttribute[Any]] = {
    TaskSortField.CREATED_AT: TaskModel.created_at,
    TaskSortField.UPDATED_AT: TaskModel.updated_at,
    TaskSortField.PROJECT: TaskModel.project_id,
    TaskSortField.STATUS: TaskModel.status,
    TaskSortField.ASSIGNEE: TaskModel.assignee_id,
    TaskSortField.PRIORITY: TaskModel.priority,
}


class TaskRepository(BaseRepository[TaskModel]):
    """Provide paginated and task-specific persistence operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Bind task operations to a request-scoped session.

        Args:
            session: Session used for task queries and persistence.
        """

        super().__init__(session, TaskModel)

    async def list_page(
        self,
        *,
        user_id: UUID,
        filters: Mapping[str, object],
        sort_field: TaskSortField,
        direction: SortDirection,
        limit: int,
        offset: int,
    ) -> tuple[list[TaskModel], int]:
        """List tasks visible through the user's project memberships.

        Args:
            user_id: User whose project memberships determine visibility.
            filters: Validated ``TaskModel`` fields and values to match.
            sort_field: Whitelisted task field used for ordering.
            direction: Ascending or descending sort direction.
            limit: Maximum tasks returned in this page.
            offset: Matching rows skipped before this page.

        Returns:
            A pair containing page items and the total matching row count.
        """

        query = (
            select(TaskModel)
            .filter_by(**filters)
            .join(
                ProjectMemberModel,
                and_(
                    ProjectMemberModel.project_id == TaskModel.project_id,
                    ProjectMemberModel.user_id == user_id,
                ),
            )
        )
        sort_column = _SORT_COLUMNS[sort_field]
        sort_order = sort_column.asc() if direction is SortDirection.ASC else sort_column.desc()
        # A unique secondary order keeps page boundaries deterministic when
        # several tasks share the selected sort value.
        id_order = TaskModel.id.asc() if direction is SortDirection.ASC else TaskModel.id.desc()

        # Reuse identical joins and filters while replacing selected task
        # columns with COUNT(*) for pagination metadata.
        count_query = query.with_only_columns(func.count())
        page_query = query.order_by(sort_order, id_order).offset(offset).limit(limit)

        total = await self.session.scalar(count_query) or 0
        items = list(await self.session.scalars(page_query))
        return items, total

    async def update_fields(
        self,
        task_id: UUID,
        changes: Mapping[str, Any],
        *,
        updated_by_id: UUID,
    ) -> TaskModel | None:
        """Apply task changes and refresh audit metadata.

        Args:
            task_id: UUID primary key of the task to update.
            changes: Task column names and replacement values.
            updated_by_id: User responsible for the update.

        Returns:
            The updated task, or ``None`` when it no longer exists.
        """

        values = {
            **changes,
            "updated_by_id": updated_by_id,
            "updated_at": datetime.now(UTC),
        }
        return await self.update(task_id, values)

    async def change_status(
        self,
        task_id: UUID,
        *,
        status: TaskStatus,
        updated_by_id: UUID,
    ) -> TaskModel | None:
        """Set a task's workflow status using last-write-wins.

        Args:
            task_id: UUID primary key of the task to update.
            status: New workflow status.
            updated_by_id: User responsible for the status change.

        Returns:
            The updated task, or ``None`` when it no longer exists.
        """

        return await self.update_fields(
            task_id,
            {"status": status},
            updated_by_id=updated_by_id,
        )
