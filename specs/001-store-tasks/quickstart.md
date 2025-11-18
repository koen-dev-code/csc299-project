# Quickstart: Store Tasks CLI (local JSON storage)

Prerequisites:

- Python 3.10+ installed
- `uv` installer available per team convention (if `uv` is not installed, `pip` can be used instead)

Install (no external dependencies required):

Using `uv` (team convention):

```powershell
uv install -r requirements.txt
```

Or with pip:

```powershell
pip install -r requirements.txt
```

Run the CLI (examples):

```powershell
python -m tasks_cli.cli create --title "Buy milk"
python -m tasks_cli.cli list
python -m tasks_cli.cli complete --id <task-id>
python -m tasks_cli.cli delete --id <task-id>
```

Configuration:

- By default, tasks are persisted to a per-user JSON file. Use `--db` or `TASKS_DB` env var to set a custom path.

Testing:

```powershell
pip install -r requirements-dev.txt
pytest -q
```

Notes:

- The default implementation is dependency-free to follow the Simplicity principle. If you prefer an improved CLI UX, install the optional `typer` package and enable the richer CLI module.
