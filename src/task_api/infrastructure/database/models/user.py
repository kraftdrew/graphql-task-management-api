"""SQLAlchemy model for API users."""

from uuid import UUID, uuid4

from sqlalchemy import Boolean, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from task_api.infrastructure.database.models.base import Base
from task_api.infrastructure.database.models.mixins.timestamp_mixin import TimestampMixin


class UserModel(TimestampMixin, Base):
    """Persist a user who can own projects and receive tasks."""

    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
    )
