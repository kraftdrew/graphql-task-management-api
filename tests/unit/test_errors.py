"""Unit tests for stable and safe GraphQL error responses."""

from graphql import GraphQLError

from task_api.presentation.graphql.errors import (
    UnauthenticatedError,
    UnauthenticatedReason,
)
from task_api.presentation.graphql.safe_graphql_router import SafeGraphQLRouter


def test_unauthenticated_error_uses_predefined_reason() -> None:
    """Expose the stable message, code, and reason for missing credentials."""

    error = UnauthenticatedError(UnauthenticatedReason.MISSING_CREDENTIALS)

    assert error.message == "A valid X-User-ID header is required."
    assert error.extensions == {
        "code": "UNAUTHENTICATED",
        "reason": "MISSING_CREDENTIALS",
    }


def test_unexpected_error_message_is_masked() -> None:
    """Replace an unexpected internal message with a client-safe error."""

    error = GraphQLError(
        "database password leaked",
        original_error=RuntimeError("database password leaked"),
    )

    safe_error = SafeGraphQLRouter._safe_error(error)

    assert safe_error.message == "Internal server error."
    assert safe_error.extensions == {"code": "INTERNAL_SERVER_ERROR"}
