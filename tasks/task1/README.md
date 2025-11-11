# Task1 CLI

A small JSON-backed command-line task manager.

Usage examples and expected outputs:

1) Add a task
Command:
```
python task.py add "Buy milk" -d "2 liters" -t groceries,errands
```
Output:
```
Added task 1: Buy milk
```

2) Add another task
Command:
```
python task.py add "Write report" -d "Finish draft" -t work
```
Output:
```
Added task 2: Write report
```

3) List all tasks
Command:
```
python task.py list
```
Example output:
```
[ ] 1: Buy milk
    2 liters
    tags: groceries, errands
[ ] 2: Write report
    Finish draft
    tags: work
```

4) Mark a task complete
Command:
```
python task.py complete 1
```
Output:
```
Marked task 1 as complete.
```

5) List only pending tasks
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

6) Search by text
Command:
```
python task.py search -q milk
```
Output:
```
[✓] 1: Buy milk
    2 liters
    tags: groceries, errands
```

7) Search by tag
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
- The data file `tasks.json` is created next to `task.py`.
- Titles are required for `add`. Use `--desc` (`-d`) for description and `--tags` (`-t`) for comma-separated tags.
- Use `--pending` with `list` to show only incomplete tasks.
