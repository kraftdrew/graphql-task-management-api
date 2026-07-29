"""Unit tests for task page navigation metadata."""

from task_api.presentation.graphql.types.outputs import TaskPageType


def test_task_page_calculates_navigation() -> None:
    """Calculate page counts and adjacent page numbers from total results."""

    result = TaskPageType.from_models([], total=49, page=2, per_page=24)

    assert result.total == 49
    assert result.pages == 3
    assert result.next_page == 3
    assert result.prev_page == 1
    assert result.last_page == 3
