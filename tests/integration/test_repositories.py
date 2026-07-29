"""PostgreSQL integration tests for generic and task repositories."""

from sqlalchemy.ext.asyncio import AsyncSession

from task_api.enums import SortDirection, TaskSortField, TaskStatus
from task_api.infrastructure.database.models import UserModel
from task_api.infrastructure.database.repositories import (
    TaskRepository,
    UserRepository,
)
from tests.support import SeedData


async def test_generic_repository_crud_survives_application_commit(
    db_session: AsyncSession,
) -> None:
    """Exercise generic CRUD after a commit handled through a test savepoint."""

    repository = UserRepository(db_session)
    user = await repository.add(
        UserModel(
            email="repository@example.com",
            display_name="Before update",
            is_active=True,
        )
    )
    await db_session.commit()

    assert await repository.get_many([user.id]) == [user]

    updated = await repository.update(user.id, {"display_name": "After update"})
    assert updated is not None
    assert updated.display_name == "After update"
    assert await repository.delete(user.id) is True
    assert await repository.delete(user.id) is False


async def test_task_repository_limits_visibility_and_returns_total(
    db_session: AsyncSession,
    seed_data: SeedData,
) -> None:
    """Exclude inaccessible projects while counting all visible matches."""

    items, total = await TaskRepository(db_session).list_page(
        user_id=seed_data.owner.id,
        filters={},
        sort_field=TaskSortField.CREATED_AT,
        direction=SortDirection.DESC,
        limit=1,
        offset=0,
    )

    assert [task.id for task in items] == [seed_data.second_task.id]
    assert total == 2


async def test_task_repository_applies_status_and_unassigned_filters(
    db_session: AsyncSession,
    seed_data: SeedData,
) -> None:
    """Combine status and null-assignee filters in the PostgreSQL query."""

    items, total = await TaskRepository(db_session).list_page(
        user_id=seed_data.owner.id,
        filters={
            "status": TaskStatus.TODO,
            "assignee_id": None,
        },
        sort_field=TaskSortField.CREATED_AT,
        direction=SortDirection.ASC,
        limit=24,
        offset=0,
    )

    assert [task.id for task in items] == [seed_data.first_task.id]
    assert total == 1
