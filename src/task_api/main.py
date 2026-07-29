"""FastAPI application exposing the GraphQL and health endpoints."""

import json
from urllib.parse import quote, urlencode

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from task_api.presentation.graphql.context import get_context
from task_api.presentation.graphql.graphiql_example import (
    EXAMPLE_HEADERS,
    EXAMPLE_QUERY,
    EXAMPLE_VARIABLES,
)
from task_api.presentation.graphql.safe_graphql_router import SafeGraphQLRouter
from task_api.presentation.graphql.schemas.schema import schema

app = FastAPI(
    title="Lush Task Management API",
    version="0.1.0",
)
app.include_router(
    SafeGraphQLRouter(
        schema=schema,
        context_getter=get_context,
        graphql_ide="graphiql",
        allow_queries_via_get=False,
    ),
    prefix="/graphql",
)


@app.get("/example", include_in_schema=False)
async def graphiql_example() -> RedirectResponse:
    """Open GraphiQL with a runnable seeded example.

    Returns:
        Redirect containing GraphiQL query, variable, and stub-header parameters.
    """

    parameters = urlencode(
        {
            "q": EXAMPLE_QUERY,
            "variables": json.dumps(EXAMPLE_VARIABLES, indent=2),
            "headers": json.dumps(EXAMPLE_HEADERS),
        },
        # GraphiQL decodes URL values with JavaScript's decodeURIComponent,
        # which understands %20 but does not translate form-style "+" spaces.
        quote_via=quote,
    )
    return RedirectResponse(url=f"/graphql?{parameters}")


@app.get("/health", tags=["operations"])
async def health() -> dict[str, str]:
    """Return a lightweight process health response.

    Returns:
        Static status payload indicating that the API process is running.
    """

    return {"status": "ok"}
