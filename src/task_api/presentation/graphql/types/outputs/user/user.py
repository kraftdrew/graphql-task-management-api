"""GraphQL user output type definition."""

from __future__ import annotations

import strawberry

from task_api.infrastructure.database.models import UserModel


@strawberry.type(
    name="User",
    description="A user who can participate in projects and tasks.",
)
class UserType:
    """Public GraphQL representation of a user."""

    id: strawberry.ID = strawberry.field(description="Unique user identifier.")
    email: str = strawberry.field(description="User email address.")
    display_name: str = strawberry.field(description="Name displayed to API clients.")
    is_active: bool = strawberry.field(
        description="Whether the user may authenticate and receive task assignments."
    )

    @classmethod
    def from_model(cls, user: UserModel) -> UserType:
        """Create a GraphQL user from a database model.

        Args:
            user: Persisted user model.

        Returns:
            Public GraphQL user representation.
        """

        return cls(
            id=strawberry.ID(str(user.id)),
            email=user.email,
            display_name=user.display_name,
            is_active=user.is_active,
        )
