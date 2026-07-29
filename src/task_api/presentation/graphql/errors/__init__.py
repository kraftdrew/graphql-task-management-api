"""Client-safe GraphQL error exports."""

from task_api.presentation.graphql.errors.auth import (
    ForbiddenError,
    UnauthenticatedError,
    UnauthenticatedReason,
)
from task_api.presentation.graphql.errors.base import TaskError
from task_api.presentation.graphql.errors.resources import (
    NotFoundError,
    ProjectNotFoundError,
    TaskNotFoundError,
)
from task_api.presentation.graphql.errors.task import (
    InvalidAssigneeError,
    InvalidStatusTransitionError,
)
from task_api.presentation.graphql.errors.validation import (
    InputValidationError,
    from_validation_error,
    invalid_id,
)

__all__ = [
    "ForbiddenError",
    "InputValidationError",
    "InvalidAssigneeError",
    "InvalidStatusTransitionError",
    "NotFoundError",
    "ProjectNotFoundError",
    "TaskError",
    "TaskNotFoundError",
    "UnauthenticatedError",
    "UnauthenticatedReason",
    "from_validation_error",
    "invalid_id",
]
