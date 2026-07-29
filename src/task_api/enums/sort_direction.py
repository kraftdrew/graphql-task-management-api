"""Supported task sort directions."""

from task_api.enums.extended_enum import ExtendedEnum


class SortDirection(ExtendedEnum):
    """Directions available when ordering task lists."""

    ASC = "asc"
    DESC = "desc"
