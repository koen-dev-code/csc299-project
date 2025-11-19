# Tasker (Typer + Neo4j)

Quick start

- Copy `.env.example` to `.env` and set `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`.
- Install dependencies (venv recommended):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt
```

Run CLI

- Add a task:

```powershell
python -m tasker add "Buy milk" -d "2 liters"
```
You can add tags by passing `-t/--tag` multiple times:

```powershell
python -m tasker add "Buy milk" -d "2 liters" -t grocery -t home
```

- List tasks:

```powershell
python -m tasker list
python -m tasker list --status todo
python -m tasker list --status done
Filter by tag:

```powershell
python -m tasker list -t grocery
```
```

- Mark done:

```powershell
python -m tasker complete <task-id>
```

- Delete:

```powershell
python -m tasker delete <task-id>
```

Shorter references

- Use the numeric index shown by `list` (1-based):

```powershell
python -m tasker complete 1
python -m tasker delete 2
```

- Use a short unique prefix of the id (first characters) instead of the full UUID:

```powershell
# If list shows '3a606c47...' you can do:
python -m tasker complete 3a606c47
```

Notes

- The project already lists `neo4j` and `typer` in `pyproject.toml`. `requirements.txt` is provided for simple `pip` installs.
- If you use Poetry/PEP 517, add these deps to your build tool as needed.
