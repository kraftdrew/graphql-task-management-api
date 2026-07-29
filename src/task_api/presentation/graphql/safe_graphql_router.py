"""FastAPI GraphQL router that prevents unexpected exception details from leaking."""

from graphql import GraphQLError
from starlette.requests import Request
from strawberry.fastapi import GraphQLRouter
from strawberry.http import GraphQLHTTPResponse
from strawberry.types import ExecutionResult

from task_api.presentation.graphql.context import GraphQLContext
from task_api.presentation.graphql.errors import TaskError


class SafeGraphQLRouter(GraphQLRouter[GraphQLContext, None]):
    """Return expected API errors while masking unexpected resolver failures."""

    async def process_result(
        self,
        request: Request,
        result: ExecutionResult,
    ) -> GraphQLHTTPResponse:
        """Prepare a GraphQL response without exposing internal exception messages.

        Args:
            request: HTTP request being processed.
            result: GraphQL execution result produced by Strawberry.

        Returns:
            JSON-compatible GraphQL response.
        """

        if result.errors:
            result.errors = [self._safe_error(error) for error in result.errors]
        return await super().process_result(request, result)

    @staticmethod
    def _safe_error(error: GraphQLError) -> GraphQLError:
        # Parsing and GraphQL validation errors have no original resolver exception
        # and are already designed for clients.
        if error.original_error is None or isinstance(error.original_error, TaskError):
            return error

        return GraphQLError(
            "Internal server error.",
            nodes=error.nodes,
            path=error.path,
            extensions={"code": "INTERNAL_SERVER_ERROR"},
        )
