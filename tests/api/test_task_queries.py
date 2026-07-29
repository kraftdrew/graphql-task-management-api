"""GraphQL API tests for visible task queries and nested fields."""

import httpx

from tests.support import SeedData


async def test_tasks_returns_only_visible_tasks_with_relationships(
    api_client: httpx.AsyncClient,
    seed_data: SeedData,
) -> None:
    """Return visible tasks and resolve their nested project and user fields."""

    response = await api_client.post(
        "/graphql",
        json={
            "query": """
                query {
                  tasks {
                    total
                    page
                    pages
                    items {
                      id
                      title
                      project { id }
                      assignee { id }
                      createdBy { id }
                      updatedBy { id }
                    }
                  }
                }
            """
        },
        headers={"X-User-ID": str(seed_data.owner.id)},
    )

    assert response.status_code == 200
    assert "errors" not in response.json()
    page = response.json()["data"]["tasks"]
    assert page["total"] == 2
    assert page["page"] == 1
    assert page["pages"] == 1
    assert [item["id"] for item in page["items"]] == [
        str(seed_data.second_task.id),
        str(seed_data.first_task.id),
    ]
    assert page["items"][0]["project"]["id"] == str(seed_data.project.id)
    assert page["items"][0]["assignee"]["id"] == str(seed_data.member.id)
    assert page["items"][1]["assignee"] is None
