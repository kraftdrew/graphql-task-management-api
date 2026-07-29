"""Shared helpers for string-valued application enums."""

from enum import Enum


class ExtendedEnum(Enum):
    """Enum base that exposes its values for SQLAlchemy constraints."""

    @classmethod
    def list_values(cls) -> list[str]:
        """Return the values used by database and GraphQL enum definitions.

        Returns:
            Raw string values in declaration order.
        """

        return [item.value for item in cls]
