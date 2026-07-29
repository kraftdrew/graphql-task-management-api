"""Input-validation errors and conversion helpers."""

from pydantic import ValidationError

from task_api.presentation.graphql.errors.base import TaskError


class InputValidationError(TaskError):
    """Expose structured Pydantic or identifier validation failures."""

    code = "VALIDATION_ERROR"

    def __init__(self, fields: list[dict[str, str]]) -> None:
        """Create an input-validation GraphQL error.

        Args:
            fields: Invalid input paths and their client-safe messages.
        """

        super().__init__(
            "Input validation failed.",
            details={"fields": fields},
        )


def from_validation_error(error: ValidationError) -> InputValidationError:
    """Convert a Pydantic validation failure to a safe GraphQL exception.

    Args:
        error: Validation failure raised while converting GraphQL input.

    Returns:
        GraphQL exception containing each invalid field and message.
    """

    return InputValidationError(
        fields=[
            {
                "field": ".".join(str(part) for part in detail["loc"]),
                "message": detail["msg"],
            }
            for detail in error.errors()
        ]
    )


def invalid_id(field: str) -> InputValidationError:
    """Create a validation exception for a malformed UUID.

    Args:
        field: GraphQL input field containing the invalid ID.

    Returns:
        GraphQL exception identifying the invalid field.
    """

    return InputValidationError(fields=[{"field": field, "message": "Must be a valid UUID."}])
