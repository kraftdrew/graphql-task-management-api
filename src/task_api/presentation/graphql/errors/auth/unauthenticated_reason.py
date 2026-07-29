"""Authentication failure reasons and their client-facing messages."""

from task_api.enums import ExtendedEnum


class UnauthenticatedReason(ExtendedEnum):
    """Specific authentication failures with centralized client messages.

    Examples:
        >>> from task_api.presentation.graphql.errors.auth.auth import (
        ...     UnauthenticatedError,
        ... )
        >>> error = UnauthenticatedError(
        ...     UnauthenticatedReason.MISSING_CREDENTIALS
        ... )
        >>> error.message
        'A valid X-User-ID header is required.'
        >>> error.extensions
        {'code': 'UNAUTHENTICATED', 'reason': 'MISSING_CREDENTIALS'}
    """

    MISSING_CREDENTIALS = "A valid X-User-ID header is required."
    UNKNOWN_OR_INACTIVE_USER = "The authenticated user is unknown or inactive."
