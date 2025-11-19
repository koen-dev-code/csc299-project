# Tasker (Typer + Neo4j)

Quick start

- Copy `.env.example` to `.env` and set `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`, and `OPENAI_API_KEY`.

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
 
Auto-suggest tags with OpenAI

If you have an OpenAI API key in `OPENAI_API_KEY`, the CLI can ask the OpenAI Chat Completions API to suggest tags for a newly created task. Use `--suggest` when adding a task:

```powershell
python -m tasker add "Buy milk" -d "2 liters" --suggest
```

The CLI will attempt to persist any suggested tags returned by the model.

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

Health checks

```powershell
python -m tasker check
```

This command verifies the Neo4j connection (using `NEO4J_*` env vars) and OpenAI (if `OPENAI_API_KEY` is set).

Delete all / completed tasks

Delete everything (asks for confirmation unless you pass `--yes`):

```powershell
python -m tasker delete-all
python -m tasker delete-all --yes
```

Delete only completed tasks (asks for confirmation unless `--yes` provided):

```powershell
python -m tasker delete-completed
python -m tasker delete-completed --yes
```

Linking tasks

Create a link from one task to another (relationship `kind` is stored as property):

```powershell
python -m tasker link <source> <target> -k depends
```

Remove a link between two tasks:

```powershell
python -m tasker unlink <source> <target> -k depends
```

Show links for a task (incoming and outgoing):

```powershell
python -m tasker links <task>
```

`<source>`, `<target>`, and `<task>` support numeric index, short id prefix, or full id (same as other commands).

DB initialization and migration

Create recommended DB constraints (task id uniqueness, tag name uniqueness):

```powershell
python -m tasker init-db
```

Migrate existing `tags` list properties into `:Tag` nodes and `HAS_TAG` relationships:

```powershell
python -m tasker migrate-tags
```

Edit tasks

Update a task's title, description, and tags. Pass `-t/--tag` multiple times to replace tags. Use `--clear-tags` to remove all tags.

```powershell
python -m tasker edit <task> --title "New title" --description "New desc" -t home -t urgent
python -m tasker edit <task> --clear-tags
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
