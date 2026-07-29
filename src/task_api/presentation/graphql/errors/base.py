"""Base exception for expected GraphQL API failures."""

from graphql import GraphQLError


class TaskError(GraphQLError):
    """Base GraphQL exception for expected task API failures."""

    code = "TASK_ERROR"

    def __init__(
        self,
        message: str,
        *,
        details: dict[str, object] | None = None,
    ) -> None:
        """Create a client-safe GraphQL error.

        Args:
            message: Message safe to expose to the API client.
            details: Optional structured values added to GraphQL extensions.
        """

        extensions: dict[str, object] = {"code": self.code}
        if details:
            extensions.update(details)
        super().__init__(message, extensions=extensions)
