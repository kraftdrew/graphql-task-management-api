"""GraphQL root schema exports."""

from task_api.presentation.graphql.schemas.mutation import Mutation
from task_api.presentation.graphql.schemas.query import Query

__all__ = ["Mutation", "Query"]
