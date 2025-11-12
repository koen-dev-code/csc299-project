# Research: CLI Task Management (Phase 0)

**Feature**: CLI Task Management (`001-cli-task-manager`)  
**Date**: 2025-11-12

## Unknowns / NEEDS CLARIFICATION

1. Installer/Dependency manager referenced as "uv" by the user — unclear what this means.

## Research Tasks & Decisions

### 1) What is "uv" for installing dependencies?

Decision: Treat "uv" as a shorthand for the project instruction to use a lightweight installer. In this design we'll use standard Python tooling by default: `pip` for installing dependencies and `venv` for virtual environments. If the user intended a different installer (for example `uv` as an alias to a package manager or an organization-specific tool), they should clarify. Marked as resolved with the assumption below.

Rationale: `pip` and `venv` are available across platforms and are standard for Python projects. Using these avoids adding another non-standard dependency and keeps the project simple.

Alternatives considered:
- `pipx` for installing CLI tools globally — rejected for per-project reproducibility
- `poetry`/`pipenv` — viable but heavier; not necessary for this small utility unless the user requests it

Action: Use `pip` + `venv` by default. Document this in quickstart.md and call out the assumption.

## Final Decisions

- Installer: `pip` and `venv` (ASSUMPTION documented)
- Language: Python (from user)
- Storage: local JSON file (from user)

## Rationale summary

Picking standard Python tooling keeps the project portable and lowers the barrier for graders and collaborators. If you intended a different installer named "uv", tell me and I will update the plan and quickstart accordingly.
