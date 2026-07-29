"""GraphQL API tests for request identity validation."""

import httpx

from tests.support import SeedData

TASK_QUERY = """
query Task($id: ID!) {
  task(id: $id) {
    id
  }
}
"""


async def test_missing_user_header_returns_unauthenticated_error(
        api_client: httpx.AsyncClient,
        seed_data: SeedData,
) -> None:
    """Return the public missing-credentials error when the header is absent."""

    response = await api_client.post(
        "/graphql",
        json={
            "query": TASK_QUERY,
            "variables": {"id": str(seed_data.first_task.id)},
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "data": None,
        "errors": [
            {
                "message": "A valid X-User-ID header is required.",
                "locations": [{"line": 3, "column": 3}],
                "path": ["task"],
                "extensions": {
                    "code": "UNAUTHENTICATED",
                    "reason": "MISSING_CREDENTIALS",
                },
            }
        ]
    }


async def test_inactive_user_returns_specific_authentication_reason(
        api_client: httpx.AsyncClient,
        seed_data: SeedData,
) -> None:
    """Reject an inactive identity with its stable authentication reason."""

    response = await api_client.post(
        "/graphql",
        json={
            "query": TASK_QUERY,
            "variables": {"id": str(seed_data.first_task.id)},
        },
        headers={"X-User-ID": str(seed_data.inactive_user.id)},
    )

    error = response.json()["errors"][0]
    assert error["extensions"] == {
        "code": "UNAUTHENTICATED",
        "reason": "UNKNOWN_OR_INACTIVE_USER",
    }
