"""Seeded operations, variables, and headers used to prefill GraphiQL.

The values mirror the Docker seed data so developers can open ``/example`` and
select successful or failing queries and mutations from GraphiQL's operation
picker. Keeping this demo content here also leaves application startup focused
on route wiring.
"""

EXAMPLE_QUERY = """\
# 1. List the seeded tasks using fields useful for a quick overview.
query ListSeededTasks($projectId: ID!) {
  tasks(filter: {projectId: $projectId}, page: 1, perPage: 10) {
    items {
      id
      title
      status
      priority
      assignee {
        id
        displayName
      }
    }
    total
    page
    pages
    perPage
    nextPage
    prevPage
    lastPage
  }
}

# 2. Create a task, then copy its returned id into the taskId variable.
mutation CreateTask($projectId: ID!, $title: String!) {
  createTask(input: {projectId: $projectId, title: $title}) {
    id
    title
    status
  }
}

# 3. List tasks again to confirm that the new task was created.
query ListTasksAfterCreate($projectId: ID!) {
  tasks(filter: {projectId: $projectId}, page: 1, perPage: 10) {
    items {
      id
      title
      description
      status
      priority
      dueAt
      createdAt
      updatedAt
      project {
        id
        name
        description
      }
      assignee {
        id
        email
        displayName
        isActive
      }
      createdBy {
        id
        email
        displayName
        isActive
      }
      updatedBy {
        id
        email
        displayName
        isActive
      }
    }
    total
    page
    pages
    perPage
    nextPage
    prevPage
    lastPage
  }
}

# 4. Assign the seeded project member to the created task.
mutation SetTaskAssignee($taskId: ID!, $assigneeId: ID!) {
  setTaskAssignee(id: $taskId, assigneeId: $assigneeId) {
    id
    assignee {
      id
      displayName
    }
  }
}

# 5. Change the created task from TODO to BLOCKED.
mutation ChangeTaskStatus($taskId: ID!, $status: TaskStatus!) {
  changeTaskStatus(id: $taskId, status: $status) {
    id
    status
  }
}

# 6. List tasks again to confirm the assignee and status changes.
query ListTasksAfterMutations($projectId: ID!) {
  tasks(filter: {projectId: $projectId}, page: 1, perPage: 10) {
    items {
      id
      title
      description
      status
      priority
      dueAt
      createdAt
      updatedAt
      project {
        id
        name
        description
      }
      assignee {
        id
        email
        displayName
        isActive
      }
      createdBy {
        id
        email
        displayName
        isActive
      }
      updatedBy {
        id
        email
        displayName
        isActive
      }
    }
    total
    page
    pages
    perPage
    nextPage
    prevPage
    lastPage
  }
}

# 7. Request a specific page. Change page and perPage in Variables to explore.
query PaginateTasks($projectId: ID!, $page: Int!, $perPage: Int!) {
  tasks(filter: {projectId: $projectId}, page: $page, perPage: $perPage) {
    items {
      id
      title
      description
      status
      priority
      dueAt
      createdAt
      updatedAt
      project {
        id
        name
        description
      }
      assignee {
        id
        email
        displayName
        isActive
      }
      createdBy {
        id
        email
        displayName
        isActive
      }
      updatedBy {
        id
        email
        displayName
        isActive
      }
    }
    total
    page
    pages
    perPage
    nextPage
    prevPage
    lastPage
  }
}

# ===== ERRORS =====
# The following operations intentionally fail to demonstrate error handling.

# 8. Expected error: UNAUTHENTICATED / MISSING_CREDENTIALS.
# Remove X-User-ID from the Headers panel before running this operation.
# Fix: restore the X-User-ID value from the prefilled Headers panel.
mutation UnauthenticatedCreate($projectId: ID!, $title: String!) {
  createTask(input: {projectId: $projectId, title: $title}) {
    id
  }
}

# 9. Expected error: VALIDATION_ERROR because the task ID is not a UUID.
# Restore the seeded owner header before running this operation.
# Fix: replace invalidTaskId with a UUID returned by CreateTask.
query InvalidTaskId($invalidTaskId: ID!) {
  task(id: $invalidTaskId) {
    id
  }
}

# 10. Expected error: INVALID_STATUS_TRANSITION for BLOCKED to DONE.
# Run ChangeTaskStatus first so the task is BLOCKED.
# Fix: change the task to IN_PROGRESS before changing it to DONE.
mutation InvalidTransition($taskId: ID!, $invalidStatus: TaskStatus!) {
  changeTaskStatus(id: $taskId, status: $invalidStatus) {
    id
    status
  }
}
"""

# These identifiers are public, deterministic development fixtures created by
# ``task_api.seed``; they are not production credentials.
EXAMPLE_VARIABLES = {
    "projectId": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
    "title": "GraphQL task demo",
    "taskId": "REPLACE_WITH_CREATED_TASK_ID",
    "assigneeId": "22222222-2222-4222-8222-222222222222",
    "status": "BLOCKED",
    "page": 1,
    "perPage": 2,
    "invalidTaskId": "not-a-uuid",
    "invalidStatus": "DONE",
}
EXAMPLE_HEADERS = {
    "X-User-ID": "11111111-1111-4111-8111-111111111111",
}
