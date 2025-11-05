# test CLI

A small JSON-backed command-line task manager.

Summary of features:
- Add tasks with title (required), optional description and comma-separated tags.
- Optionally assign a date to a task.
- List tasks, filter to pending only, and sort by created, date, id or title.
- Search tasks by text or tag.
- Mark tasks complete, remove a single task, or purge all completed tasks.

Accepted date formats:
- YYYY-MM-DD (recommended)
- ISO datetime (e.g. 2025-12-01T14:30:00)

Usage examples and expected outputs:

1) Add a task (with date)
Command:
```
python task.py add "Buy milk" -d "2 liters" -t groceries,errands -D 2025-12-01
```
Output:
```
Added task 1: Buy milk
```

2) Add another task (no date)
Command:
```
python task.py add "Write report" -d "Finish draft" -t work
```
Output:
```
Added task 2: Write report
```

3) List all tasks (default sort = created)
Command:
```
python task.py list
```
Example output:
```
[ ] 1: Buy milk
    2 liters
    date: 2025-12-01
    tags: groceries, errands
[ ] 2: Write report
    Finish draft
    tags: work
```

4) List tasks sorted by date
Command:
```
python task.py list --sort date
```
Example output (tasks ordered by the task 'date' field):
```
[ ] 1: Buy milk
    2 liters
    date: 2025-12-01
    tags: groceries, errands
[ ] 2: Write report
    Finish draft
    tags: work
```

5) Mark a task complete
Command:
```
python task.py complete 1
```
Output:
```
Marked task 1 as complete.
```

6) Remove a single task
Command:
```
python task.py remove 2
```
Output:
```
Removed task 2: Write report
```

7) Purge all completed tasks
Command:
```
python task.py purge-completed
```
Output (example):
```
Removed 1 completed task(s).
```

8) List only pending tasks
Command:
```
python task.py list --pending
```
Example output:
```
[ ] 2: Write report
    Finish draft
    tags: work
```

9) Search by text
Command:
```
python task.py search -q milk
```
Output:
```
[✓] 1: Buy milk
    2 liters
    date: 2025-12-01
    tags: groceries, errands
```

10) Search by tag
Command:
```
python task.py search --tag work
```
Output:
```
[ ] 2: Write report
    Finish draft
    tags: work
```

Notes:
- The data file `test.json` is created next to `test.py`.
- Use `--date` or `-D` when adding to assign a date (YYYY-MM-DD or ISO). Dates are shown in the listing if present.
- Use `--sort` with `list` to choose the sort field: created, date, id, or title.
- Use `--pending` with `list` to show only incomplete tasks.
- Use `remove <id>` to delete a single task and `purge-completed` to delete all completed tasks.
