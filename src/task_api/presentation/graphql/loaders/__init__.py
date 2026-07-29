"""Public factories for request-scoped GraphQL model loaders.

Import loader factories from this package when constructing ``GraphQLContext``;
the generic implementation remains an internal construction helper.

Example:
    >>> from task_api.presentation.graphql.loaders import (
    ...     create_project_loader,
    ...     create_user_loader,
    ... )
"""

from task_api.presentation.graphql.loaders.project_loader import create_project_loader
from task_api.presentation.graphql.loaders.user_loader import create_user_loader

__all__ = ["create_project_loader", "create_user_loader"]
