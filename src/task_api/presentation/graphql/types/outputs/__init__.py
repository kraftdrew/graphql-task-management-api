"""GraphQL output type exports."""

from task_api.presentation.graphql.types.outputs.project import ProjectType
from task_api.presentation.graphql.types.outputs.results import DeleteTaskSuccess
from task_api.presentation.graphql.types.outputs.task import TaskPageType, TaskType
from task_api.presentation.graphql.types.outputs.user import UserType

__all__ = [
    "DeleteTaskSuccess",
    "ProjectType",
    "TaskPageType",
    "TaskType",
    "UserType",
]
