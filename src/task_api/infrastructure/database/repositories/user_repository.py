"""User database persistence operations."""

from sqlalchemy.ext.asyncio import AsyncSession

from task_api.infrastructure.database.models import UserModel
from task_api.infrastructure.database.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[UserModel]):
    """Provide shared persistence operations for users."""

    def __init__(self, session: AsyncSession) -> None:
        """Bind user operations to a request-scoped session.

        Args:
            session: Session used for user queries and persistence.
        """

        super().__init__(session, UserModel)
