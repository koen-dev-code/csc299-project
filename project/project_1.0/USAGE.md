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

- List tasks:

```powershell
python -m tasker list
python -m tasker list --status todo
python -m tasker list --status done
```

- Mark done:

```powershell
python -m tasker complete <task-id>
```

- Delete:

```powershell
python -m tasker delete <task-id>
```

Notes

- The project already lists `neo4j` and `typer` in `pyproject.toml`. `requirements.txt` is provided for simple `pip` installs.
- If you use Poetry/PEP 517, add these deps to your build tool as needed.
