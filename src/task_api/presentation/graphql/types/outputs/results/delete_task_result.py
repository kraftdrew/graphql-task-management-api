"""GraphQL output type for successful task deletion."""

import strawberry


@strawberry.type(description="Confirmation that a task was deleted.")
class DeleteTaskSuccess:
    """Successful task deletion result."""

    deleted_task_id: strawberry.ID = strawberry.field(description="Identifier of the deleted task.")
