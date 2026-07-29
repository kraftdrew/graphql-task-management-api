"""Seed deterministic users, a project, memberships, and tasks for development."""

import asyncio
from uuid import UUID

from sqlalchemy import select

from task_api.enums import ProjectRole, TaskPriority, TaskStatus
from task_api.infrastructure.database.models import (
    ProjectMemberModel,
    ProjectModel,
    TaskModel,
    UserModel,
)
from task_api.infrastructure.database.session import session_factory

OWNER_ID = UUID("11111111-1111-4111-8111-111111111111")
MEMBER_ID = UUID("22222222-2222-4222-8222-222222222222")
PROJECT_ID = UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa")
TASK_IDS = tuple(
    UUID(f"00000000-0000-4000-8000-{task_number:012d}")
    for task_number in range(1, 21)
)


async def seed() -> None:
    """Insert deterministic local demonstration records.

    Existing users, project memberships, and demo tasks are preserved, making
    the operation safe to run repeatedly.
    """

    async with session_factory() as session:
        if await session.scalar(select(UserModel.id).where(UserModel.id == OWNER_ID)) is None:
            session.add(
                UserModel(
                    id=OWNER_ID,
                    email="owner@example.com",
                    display_name="Project Owner",
                )
            )
        if await session.scalar(select(UserModel.id).where(UserModel.id == MEMBER_ID)) is None:
            session.add(
                UserModel(
                    id=MEMBER_ID,
                    email="member@example.com",
                    display_name="Project Member",
                )
            )
        await session.flush()

        if (
            await session.scalar(select(ProjectModel.id).where(ProjectModel.id == PROJECT_ID))
            is None
        ):
            session.add(
                ProjectModel(
                    id=PROJECT_ID,
                    name="Demo Project",
                    description="Local development project",
                    created_by_id=OWNER_ID,
                )
            )
        await session.flush()

        for user_id, role in (
            (OWNER_ID, ProjectRole.OWNER),
            (MEMBER_ID, ProjectRole.MEMBER),
        ):
            membership = await session.get(
                ProjectMemberModel,
                {"project_id": PROJECT_ID, "user_id": user_id},
            )
            if membership is None:
                session.add(
                    ProjectMemberModel(
                        project_id=PROJECT_ID,
                        user_id=user_id,
                        role=role,
                    )
                )

        existing_task_ids = set(
            (
                await session.scalars(
                    select(TaskModel.id).where(TaskModel.id.in_(TASK_IDS))
                )
            ).all()
        )
        statuses = tuple(TaskStatus)
        priorities = tuple(TaskPriority)
        for task_number, task_id in enumerate(TASK_IDS, start=1):
            if task_id in existing_task_ids:
                continue
            session.add(
                TaskModel(
                    id=task_id,
                    project_id=PROJECT_ID,
                    title=f"Demo task {task_number:02d}",
                    description=f"Seeded task for pagination example {task_number}.",
                    status=statuses[(task_number - 1) % len(statuses)],
                    priority=priorities[(task_number - 1) % len(priorities)],
                    assignee_id=MEMBER_ID if task_number % 2 == 0 else None,
                    created_by_id=OWNER_ID,
                    updated_by_id=OWNER_ID,
                )
            )
        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed())
