"""Task assignment and workflow errors."""

from task_api.enums import TaskStatus
from task_api.presentation.graphql.errors.base import TaskError


class InvalidAssigneeError(TaskError):
    """Signal that a requested assignee cannot receive the task."""

    code = "INVALID_ASSIGNEE"

    def __init__(self) -> None:
        """Create the standard invalid-assignee error."""

        super().__init__("Assignee must be an active member of the task's project.")


class InvalidStatusTransitionError(TaskError):
    """Signal that a requested workflow transition is not allowed."""

    code = "INVALID_STATUS_TRANSITION"

    def __init__(self, current: TaskStatus, requested: TaskStatus) -> None:
        """Describe a rejected workflow transition.

        Args:
            current: Task status observed before the request.
            requested: Status requested by the client.
        """

        super().__init__(
            f"Cannot change task status from {current.value} to {requested.value}.",
            details={
                "currentStatus": current.value,
                "requestedStatus": requested.value,
            },
        )
