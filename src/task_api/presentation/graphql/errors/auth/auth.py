"""Authentication and authorization errors."""

from task_api.presentation.graphql.errors.auth.unauthenticated_reason import (
    UnauthenticatedReason,
)
from task_api.presentation.graphql.errors.base import TaskError


class UnauthenticatedError(TaskError):
    """Signal missing, malformed, unknown, or inactive user identity."""

    code = "UNAUTHENTICATED"

    def __init__(self, reason: UnauthenticatedReason) -> None:
        """Create an authentication error from a predefined reason.

        Args:
            reason: Predefined failure reason containing the client-safe message.

        Examples:
            >>> error = UnauthenticatedError(
            ...     UnauthenticatedReason.MISSING_CREDENTIALS
            ... )
            >>> error.message
            'A valid X-User-ID header is required.'
            >>> error.extensions
            {'code': 'UNAUTHENTICATED', 'reason': 'MISSING_CREDENTIALS'}
        """

        super().__init__(
            reason.value,
            details={"reason": reason.name},
        )


class ForbiddenError(TaskError):
    """Signal that the authenticated user lacks permission."""

    code = "FORBIDDEN"

    def __init__(self) -> None:
        """Create the standard forbidden error.

        Examples:
            >>> error = ForbiddenError()
            >>> error.message
            'You do not have permission to perform this operation.'
            >>> error.extensions
            {'code': 'FORBIDDEN'}
        """

        super().__init__("You do not have permission to perform this operation.")
