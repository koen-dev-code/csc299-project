# Quickstart: CLI Task Management

**Feature**: CLI Task Management (`001-cli-task-manager`)  
**Date**: 2025-11-12

## Setup (assumptions)

This quickstart assumes Python 3.8+ is installed and that the project uses `venv`
for virtual environments and `pip` for installing dependencies (see research.md
for rationale; the user referenced "uv" — we assumed `pip` unless you specify
otherwise).

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1    # Windows PowerShell
```

2. Install dependencies (if any):

```powershell
pip install -r requirements.txt
```

3. Run the CLI (examples):

```powershell
# Add a task
python -m taskcli add "Buy milk"

# List tasks
python -m taskcli list

# Delete a task
python -m taskcli delete <id>
```

If you prefer a different tooling (poetry, pipx, or a custom installer named "uv"),
provide guidance and I will update these steps.
