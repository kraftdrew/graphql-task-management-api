"""Project membership roles."""

from task_api.enums.extended_enum import ExtendedEnum


class ProjectRole(ExtendedEnum):
    """Roles controlling a user's permissions within a project."""

    OWNER = "owner"
    MEMBER = "member"
