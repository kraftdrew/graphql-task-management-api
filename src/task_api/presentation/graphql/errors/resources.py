"""Errors for resources that are absent or hidden from the client."""

from task_api.presentation.graphql.errors.base import TaskError


class NotFoundError(TaskError):
    """Base exception for resources hidden or absent from the API."""

    code = "NOT_FOUND"


class ProjectNotFoundError(NotFoundError):
    """Signal that a project does not exist."""

    def __init__(self) -> None:
        """Create the standard missing-project error."""

        super().__init__("Project was not found.")


class TaskNotFoundError(NotFoundError):
    """Signal that a task does not exist."""

    def __init__(self) -> None:
        """Create the standard missing-task error."""

        super().__init__("Task was not found.")
