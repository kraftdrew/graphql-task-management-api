"""Shared test data constructed inside rollback-isolated transactions."""

from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from task_api.enums import ProjectRole, TaskPriority, TaskStatus
from task_api.infrastructure.database.models import (
    ProjectMemberModel,
    ProjectModel,
    TaskModel,
    UserModel,
)


@dataclass(frozen=True)
class SeedData:
    """Models representing common authorization and task scenarios."""

    owner: UserModel
    member: UserModel
    outsider: UserModel
    inactive_user: UserModel
    project: ProjectModel
    other_project: ProjectModel
    first_task: TaskModel
    second_task: TaskModel
    hidden_task: TaskModel


async def create_seed_data(session: AsyncSession) -> SeedData:
    """Insert a small related dataset into the current test transaction.

    Args:
        session: Rollback-isolated database session.

    Returns:
        Persisted users, projects, memberships, and tasks.
    """

    owner = UserModel(
        email="owner@example.com",
        display_name="Owner",
        is_active=True,
    )
    member = UserModel(
        email="member@example.com",
        display_name="Member",
        is_active=True,
    )
    outsider = UserModel(
        email="outsider@example.com",
        display_name="Outsider",
        is_active=True,
    )
    inactive_user = UserModel(
        email="inactive@example.com",
        display_name="Inactive",
        is_active=False,
    )
    session.add_all([owner, member, outsider, inactive_user])
    await session.flush()

    project = ProjectModel(
        name="Visible project",
        description="Project visible to owner and member.",
        created_by_id=owner.id,
    )
    other_project = ProjectModel(
        name="Hidden project",
        description=None,
        created_by_id=outsider.id,
    )
    session.add_all([project, other_project])
    await session.flush()

    session.add_all(
        [
            ProjectMemberModel(
                project_id=project.id,
                user_id=owner.id,
                role=ProjectRole.OWNER,
            ),
            ProjectMemberModel(
                project_id=project.id,
                user_id=member.id,
                role=ProjectRole.MEMBER,
            ),
            ProjectMemberModel(
                project_id=other_project.id,
                user_id=outsider.id,
                role=ProjectRole.OWNER,
            ),
        ]
    )

    first_task = TaskModel(
        project_id=project.id,
        title="First visible task",
        description=None,
        status=TaskStatus.TODO,
        priority=TaskPriority.MEDIUM,
        assignee_id=None,
        created_by_id=owner.id,
        updated_by_id=owner.id,
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
        updated_at=datetime(2026, 1, 1, tzinfo=UTC),
    )
    second_task = TaskModel(
        project_id=project.id,
        title="Second visible task",
        description="Assigned task.",
        status=TaskStatus.IN_PROGRESS,
        priority=TaskPriority.HIGH,
        assignee_id=member.id,
        created_by_id=owner.id,
        updated_by_id=member.id,
        created_at=datetime(2026, 1, 2, tzinfo=UTC),
        updated_at=datetime(2026, 1, 2, tzinfo=UTC),
    )
    hidden_task = TaskModel(
        project_id=other_project.id,
        title="Hidden task",
        description=None,
        status=TaskStatus.DONE,
        priority=TaskPriority.LOW,
        assignee_id=outsider.id,
        created_by_id=outsider.id,
        updated_by_id=outsider.id,
        created_at=datetime(2026, 1, 3, tzinfo=UTC),
        updated_at=datetime(2026, 1, 3, tzinfo=UTC),
    )
    session.add_all([first_task, second_task, hidden_task])
    await session.flush()

    return SeedData(
        owner=owner,
        member=member,
        outsider=outsider,
        inactive_user=inactive_user,
        project=project,
        other_project=other_project,
        first_task=first_task,
        second_task=second_task,
        hidden_task=hidden_task,
    )
