"""Task priority levels."""

from task_api.enums.extended_enum import ExtendedEnum


class TaskPriority(ExtendedEnum):
    """Priorities available for task classification."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
