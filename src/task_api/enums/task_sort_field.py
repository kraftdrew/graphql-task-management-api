"""Fields available for sorting task lists."""

from task_api.enums.extended_enum import ExtendedEnum


class TaskSortField(ExtendedEnum):
    """Whitelisted task fields exposed through GraphQL sorting."""

    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    PROJECT = "project"
    STATUS = "status"
    ASSIGNEE = "assignee"
    PRIORITY = "priority"
