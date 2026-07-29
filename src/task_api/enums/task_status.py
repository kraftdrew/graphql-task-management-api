"""Task workflow statuses."""

from task_api.enums.extended_enum import ExtendedEnum


class TaskStatus(ExtendedEnum):
    """States available in the task workflow."""

    TODO = "todo"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    DONE = "done"
