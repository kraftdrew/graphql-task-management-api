"""GraphQL project output type definition."""

from __future__ import annotations

import strawberry

from task_api.infrastructure.database.models import ProjectModel


@strawberry.type(
    name="Project",
    description="A project containing tasks and members.",
)
class ProjectType:
    """Public GraphQL representation of a project."""

    id: strawberry.ID = strawberry.field(description="Unique project identifier.")
    name: str = strawberry.field(description="Project name.")
    description: str | None = strawberry.field(description="Optional project details.")

    @classmethod
    def from_model(cls, project: ProjectModel) -> ProjectType:
        """Create a GraphQL project from a database model.

        Args:
            project: Persisted project model.

        Returns:
            Public GraphQL project representation.
        """

        return cls(
            id=strawberry.ID(str(project.id)),
            name=project.name,
            description=project.description,
        )
