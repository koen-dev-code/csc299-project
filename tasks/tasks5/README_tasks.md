# Tasks CLI (local JSON storage)

This is a minimal Python CLI application to create, list, update, complete and delete tasks stored in a JSON document.

Install (developer):

```powershell
uv install -r requirements-dev.txt
```

Run tests:

```powershell
pytest -q
```

Run CLI examples:

```powershell
python -m tasks_cli.cli create --title "Buy milk"
python -m tasks_cli.cli list
```

Configuration:

- Set `TASKS_DB` environment variable or pass `--db` to the CLI to use a custom JSON file path.
