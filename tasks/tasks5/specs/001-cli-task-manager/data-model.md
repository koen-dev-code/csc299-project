# Data Model: CLI Task Management

**Feature**: CLI Task Management (`001-cli-task-manager`)  
**Date**: 2025-11-12

## Entities

### Task
- id: string (persistent unique identifier; could be UUID or incremental integer stored as string)
- title: string (required, non-empty)
- description: string (optional)
- created_at: ISO-8601 timestamp (string)
- completed: boolean (optional; default false)

## Storage Layout (JSON document)

The tasks are stored in a JSON file with the following structure:

{
  "tasks": [
    {
      "id": "<id>",
      "title": "...",
      "description": "...",
      "created_at": "2025-11-12T12:34:56Z",
      "completed": false
    }
  ]
}

## Validation Rules
- `title` MUST be non-empty and trimmed to remove leading/trailing whitespace.
- `id` MUST be unique across tasks.
- `created_at` MUST be a valid ISO-8601 timestamp when present.
- Operations that mutate storage MUST ensure atomic writes (write-then-rename pattern)
  or use a simple file lock to avoid corruption.

## Notes
- For the MVP single-user CLI, a simple file-per-repo JSON is sufficient. If multiple
  concurrent processes are anticipated later, a small locking strategy or switching
  to a lightweight DB is recommended.
