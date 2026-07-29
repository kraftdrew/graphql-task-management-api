"""Unit tests for validated GraphQL task input conversion."""

from uuid import uuid4

import pytest
from pydantic import ValidationError

from task_api.presentation.graphql.types.inputs import (
    CreateTaskData,
    TaskFilterInput,
    UpdateTaskInput,
    page_data,
)


@pytest.mark.parametrize("title", ["", "   ", "x" * 201])
def test_create_task_rejects_invalid_title(title: str) -> None:
    """Reject blank, whitespace-only, and overlong creation titles."""

    with pytest.raises(ValidationError):
        CreateTaskData.model_validate(
            {
                "project_id": uuid4(),
                "title": title,
            }
        )


def test_update_task_requires_at_least_one_change() -> None:
    """Reject an update input that does not supply any editable field."""

    with pytest.raises(ValidationError, match="At least one field"):
        UpdateTaskInput().to_data()


def test_update_task_preserves_explicit_null_description() -> None:
    """Keep an explicit null so clients can remove an existing description."""

    data = UpdateTaskInput(description=None).to_data()

    assert data.changes() == {"description": None}


def test_null_assignee_filter_selects_unassigned_tasks() -> None:
    """Distinguish an explicit null assignee from an omitted filter."""

    filters = TaskFilterInput(assignee_id=None).to_data()

    assert filters.query_values() == {"assignee_id": None}


@pytest.mark.parametrize(
    ("page", "per_page"),
    [
        (0, 24),
        (1, 0),
        (1, 101),
    ],
)
def test_page_data_rejects_values_outside_limits(page: int, per_page: int) -> None:
    """Reject page numbers and page sizes outside the public API limits."""

    with pytest.raises(ValidationError):
        page_data(page, per_page)
