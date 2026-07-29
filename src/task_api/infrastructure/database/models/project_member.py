"""SQLAlchemy model for project memberships."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from task_api.enums import ProjectRole
from task_api.infrastructure.database.models.base import Base


class ProjectMemberModel(Base):
    """Associate a user with a project and role."""

    __tablename__ = "project_members"
    __table_args__ = (Index("ix_project_members_user_project", "user_id", "project_id"),)

    project_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        primary_key=True,
    )
    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    role: Mapped[ProjectRole] = mapped_column(
        Enum(
            ProjectRole,
            name="project_role",
            native_enum=False,
            values_callable=lambda enum: enum.list_values(),
            create_constraint=True,
        ),
        nullable=False,
        default=ProjectRole.MEMBER,
        server_default=ProjectRole.MEMBER.value,
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
