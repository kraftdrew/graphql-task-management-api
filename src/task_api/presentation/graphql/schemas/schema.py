"""Assemble the root query and mutation classes into the executable schema."""

import strawberry

from task_api.presentation.graphql.schemas import Mutation, Query

# FastAPI's GraphQLRouter executes this schema for requests to /graphql.
schema = strawberry.Schema(query=Query, mutation=Mutation)
