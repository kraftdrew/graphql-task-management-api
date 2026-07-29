"""GraphQL API tests for task creation, workflow, and deletion."""

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from task_api.infrastructure.database.models import TaskModel
from tests.support import SeedData


async def test_create_task_commits_inside_rollback_isolated_session(
    api_client: httpx.AsyncClient,
    db_session: AsyncSession,
    seed_data: SeedData,
) -> None:
    """Persist a GraphQL-created task despite the fixture-owned transaction."""

    response = await api_client.post(
        "/graphql",
        json={
            "query": """
                mutation CreateTask($input: CreateTaskInput!) {
                  createTask(input: $input) {
                    id
                    title
                    status
                    priority
                    assignee { id }
                  }
                }
            """,
            "variables": {
                "input": {
                    "projectId": str(seed_data.project.id),
                    "title": "Created through GraphQL",
                    "priority": "HIGH",
                    "assigneeId": str(seed_data.member.id),
                }
            },
        },
        headers={"X-User-ID": str(seed_data.owner.id)},
    )

    assert "errors" not in response.json()
    task_data = response.json()["data"]["createTask"]
    assert task_data["status"] == "TODO"
    assert task_data["priority"] == "HIGH"
    assert task_data["assignee"]["id"] == str(seed_data.member.id)
    assert await db_session.get(TaskModel, task_data["id"]) is not None


async def test_invalid_status_transition_returns_structured_error(
    api_client: httpx.AsyncClient,
    seed_data: SeedData,
) -> None:
    """Return stable transition details when a workflow move is disallowed."""

    response = await api_client.post(
        "/graphql",
        json={
            "query": """
                mutation ChangeStatus($id: ID!, $status: TaskStatus!) {
                  changeTaskStatus(id: $id, status: $status) {
                    id
                  }
                }
            """,
            "variables": {
                "id": str(seed_data.first_task.id),
                "status": "DONE",
            },
        },
        headers={"X-User-ID": str(seed_data.owner.id)},
    )

    error = response.json()["errors"][0]
    assert error["extensions"] == {
        "code": "INVALID_STATUS_TRANSITION",
        "currentStatus": "todo",
        "requestedStatus": "done",
    }


async def test_only_project_owner_can_delete_task(
    api_client: httpx.AsyncClient,
    seed_data: SeedData,
) -> None:
    """Forbid member deletion while allowing the owning project user."""

    mutation = """
        mutation DeleteTask($id: ID!) {
          deleteTask(id: $id) {
            deletedTaskId
          }
        }
    """
    variables = {"id": str(seed_data.first_task.id)}

    forbidden_response = await api_client.post(
        "/graphql",
        json={"query": mutation, "variables": variables},
        headers={"X-User-ID": str(seed_data.member.id)},
    )
    assert forbidden_response.json()["errors"][0]["extensions"] == {"code": "FORBIDDEN"}

    owner_response = await api_client.post(
        "/graphql",
        json={"query": mutation, "variables": variables},
        headers={"X-User-ID": str(seed_data.owner.id)},
    )
    assert owner_response.json()["data"]["deleteTask"] == {
        "deletedTaskId": str(seed_data.first_task.id)
    }
