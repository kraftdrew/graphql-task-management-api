"""Task GraphQL input types and validated data models."""

from datetime import datetime
from typing import Annotated
from uuid import UUID

import strawberry
from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, StringConstraints, model_validator
from strawberry import UNSET
from strawberry.types.unset import UnsetType

from task_api.enums import SortDirection, TaskPriority, TaskSortField, TaskStatus

Title = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
Description = Annotated[str, StringConstraints(strip_whitespace=True, max_length=10_000)]


class InputData(BaseModel):
    """Base for validated data passed from GraphQL to resolvers."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class CreateTaskData(InputData):
    """Validated values required to create a task."""

    project_id: UUID
    title: Title
    description: Description | None = None
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee_id: UUID | None = None
    due_at: AwareDatetime | None = None


class UpdateTaskData(InputData):
    """Validated partial changes for an existing task."""

    title: Title | None = None
    description: Description | None = None
    priority: TaskPriority | None = None
    due_at: AwareDatetime | None = None

    @model_validator(mode="after")
    def require_change(self) -> "UpdateTaskData":
        """Validate that an update contains at least one legal change.

        Returns:
            The validated update data.

        Raises:
            ValueError: If no field is supplied or a required field is null.
        """

        if not self.model_fields_set:
            raise ValueError("At least one field must be supplied.")
        if "title" in self.model_fields_set and self.title is None:
            raise ValueError("Title cannot be null.")
        if "priority" in self.model_fields_set and self.priority is None:
            raise ValueError("Priority cannot be null.")
        return self

    def changes(self) -> dict[str, object]:
        """Build persistence changes from explicitly supplied fields.

        Returns:
            Mapping of task column names to validated replacement values.
        """

        return {
            field: getattr(self, field)
            for field in self.model_fields_set
            if field in {"title", "description", "priority", "due_at"}
        }


class TaskFilterData(InputData):
    """Validated optional filters for task listing."""

    project_id: UUID | None = None
    status: TaskStatus | None = None
    assignee_id: UUID | None = None

    def query_values(self) -> dict[str, object]:
        """Build query filters from explicitly supplied fields.

        Returns:
            Mapping of task column names to validated filter values.
        """

        return self.model_dump(exclude_unset=True)


class TaskSortData(InputData):
    """Validated field and direction for task ordering."""

    field: TaskSortField = TaskSortField.CREATED_AT
    direction: SortDirection = SortDirection.DESC


class TaskPageData(InputData):
    """Validated offset-pagination inputs."""

    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=24, ge=1, le=100)


# Register the application enums as GraphQL enums.
TaskStatusType = strawberry.enum(
    TaskStatus,
    name="TaskStatus",
    description="Workflow status of a task.",
)
TaskPriorityType = strawberry.enum(
    TaskPriority,
    name="TaskPriority",
    description="Importance assigned to a task.",
)
TaskSortFieldType = strawberry.enum(
    TaskSortField,
    name="TaskSortField",
    description="Task field available for list ordering.",
)
SortDirectionType = strawberry.enum(
    SortDirection,
    name="SortDirection",
    description="Ascending or descending list order.",
)


@strawberry.input(description="Values used to create a task.")
class CreateTaskInput:
    """GraphQL input used to create a task."""

    project_id: strawberry.ID = strawberry.field(
        description="Project in which the task will be created."
    )
    title: str = strawberry.field(description="Task title containing 1 to 200 characters.")
    description: str | None = strawberry.field(
        default=None,
        description="Optional task details containing at most 10,000 characters.",
    )
    priority: TaskPriority = strawberry.field(
        default=TaskPriority.MEDIUM,
        description="Initial task priority.",
    )
    assignee_id: strawberry.ID | None = strawberry.field(
        default=None,
        description="Optional active project member to assign.",
    )
    due_at: datetime | None = strawberry.field(
        default=None,
        description="Optional deadline for completing the task.",
    )


@strawberry.input(description="Editable values of an existing task.")
class UpdateTaskInput:
    """GraphQL input containing optional task changes."""

    # UNSET distinguishes an omitted field from an explicit null.
    title: str | None | UnsetType = strawberry.field(
        default=UNSET,
        description="Replacement title containing 1 to 200 characters.",
    )
    description: str | None | UnsetType = strawberry.field(
        default=UNSET,
        description="Replacement details, or null to remove them.",
    )
    priority: TaskPriority | None | UnsetType = strawberry.field(
        default=UNSET,
        description="Replacement task priority.",
    )
    due_at: datetime | None | UnsetType = strawberry.field(
        default=UNSET,
        description="Replacement deadline, or null to remove it.",
    )

    def to_data(self) -> UpdateTaskData:
        """Convert explicitly supplied GraphQL changes to validated data.

        Returns:
            Validated partial task update.

        Raises:
            ValidationError: If the update is empty or contains invalid values.
        """

        values = {
            name: value
            for name in ("title", "description", "priority", "due_at")
            if (value := getattr(self, name)) is not UNSET
        }
        return UpdateTaskData.model_validate(values)


@strawberry.input(description="Optional filters applied to the task list.")
class TaskFilterInput:
    """GraphQL input containing optional task filters."""

    project_id: strawberry.ID | None | UnsetType = strawberry.field(
        default=UNSET,
        description="Return only tasks in this project.",
    )
    status: TaskStatus | None | UnsetType = strawberry.field(
        default=UNSET,
        description="Return only tasks with this status.",
    )
    assignee_id: strawberry.ID | None | UnsetType = strawberry.field(
        default=UNSET,
        description="Return tasks assigned to this user; null selects unassigned tasks.",
    )

    def to_data(self) -> TaskFilterData:
        """Convert explicitly supplied GraphQL filters to validated data.

        Returns:
            Validated filters with omitted fields preserved as omitted.

        Raises:
            ValidationError: If an ID or enum filter is invalid.
        """

        values: dict[str, object] = {}
        for name in ("project_id", "status", "assignee_id"):
            value = getattr(self, name)
            # UNSET means the client omitted a filter. Explicit None remains
            # present so ``assigneeId: null`` selects unassigned tasks.
            if value is not UNSET:
                values[name] = (
                    str(value)
                    if name in {"project_id", "assignee_id"} and value is not None
                    else value
                )
        return TaskFilterData.model_validate(values)


@strawberry.input(description="Ordering applied to the task list.")
class TaskSortInput:
    """GraphQL input controlling task ordering."""

    field: TaskSortField = strawberry.field(
        default=TaskSortField.CREATED_AT,
        description="Task field used for ordering.",
    )
    direction: SortDirection = strawberry.field(
        default=SortDirection.DESC,
        description="Direction in which ordered tasks are returned.",
    )

    def to_data(self) -> TaskSortData:
        """Convert GraphQL sorting to validated repository values.

        Returns:
            Validated sort field and direction.
        """

        return TaskSortData(field=self.field, direction=self.direction)


def page_data(page: int, per_page: int) -> TaskPageData:
    """Validate page-number pagination arguments.

    Args:
        page: One-based page number.
        per_page: Maximum tasks requested per page.

    Returns:
        Validated pagination values.

    Raises:
        ValidationError: If either value falls outside its allowed range.
    """

    return TaskPageData(page=page, per_page=per_page)
