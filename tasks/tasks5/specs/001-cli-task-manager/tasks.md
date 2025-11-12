---
description: "Task list for CLI Task Management (001-cli-task-manager)"
---

# Tasks: CLI Task Management

**Input**: Design and plan files in `specs/001-cli-task-manager/`
**Prerequisites**: `plan.md` (required), `spec.md` (required for user stories), `research.md`, `data-model.md`, `contracts/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project directory structure per implementation plan (create `src/taskcli/`, `tests/`, `tasks/tasks5/.github/workflows/` if missing) — ensure `src/taskcli/__init__.py` exists and `src/taskcli/__main__.py` entrypoint present
- [ ] T002 [P] Initialize Python virtual environment and document usage in `tasks/tasks5/quickstart.md` (create `.venv/` via `python -m venv .venv` in local dev instructions)
- [ ] T003 Create `requirements.txt` at project root `tasks/tasks5/requirements.txt` and document that MVP uses only stdlib (file already present; verify contents)
- [ ] T004 [P] Add module entrypoint so the package is runnable via `python -m taskcli` (`src/taskcli/__main__.py`) — file path: `tasks/tasks5/src/taskcli/__main__.py`
- [ ] T005 Add a minimal README for the feature at `tasks/tasks5/README.md` describing how to run tests and CLI (already present; verify and update if needed)

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

- [ ] T006 Create JSON storage layout documentation at `tasks/tasks5/specs/001-cli-task-manager/data-model.md` (verify structure and validation rules)
- [ ] T007 [P] Implement atomic write helper for JSON storage (`tasks/tasks5/src/taskcli/store.py`) — ensure write-then-rename pattern and fallback for JSON decode errors
- [ ] T008 Create `tests/test_store.py` with unit tests for add/list/delete behavior (file: `tasks/tasks5/tests/test_store.py`)
- [ ] T009 Configure CI to run unit tests on PRs and pushes (workflow file: `tasks/tasks5/.github/workflows/ci.yml` and repo-level `.github/workflows/ci.yml`) — ensure tests run from `tasks/tasks5`
- [ ] T010 [P] Document default data file path and how to override via environment variable in `tasks/tasks5/README.md` (document `TASKCLI_DATA`)

**Checkpoint**: Foundation ready — user story implementation can proceed

## Phase 3: User Story 1 - Add Task (Priority: P1) 🎯 MVP

**Goal**: Allow users to add a task with a title and optional description and persist it

**Independent Test**: Use `python -m taskcli add "Buy milk"` then `python -m taskcli list` and verify the new task appears (see acceptance scenarios in `specs/001-cli-task-manager/spec.md`)

### Tests for User Story 1
- [ ] T011 [US1] Create unit test: verify `add_task(title)` returns an id and that `list_tasks()` includes the new task (file: `tasks/tasks5/tests/test_store.py`)

### Implementation for User Story 1
- [ ] T012 [US1] Implement `add_task(title, description)` in `tasks/tasks5/src/taskcli/store.py` (ensure validation: non-empty title)
- [ ] T013 [US1] Implement CLI `add` subcommand in `tasks/tasks5/src/taskcli/cli.py` to call `add_task` and print id + confirmation
- [X] T014 [US1] Add integration test that runs the CLI `add` (via `python -m taskcli add`) and checks `list` output (file: `tasks/tasks5/tests/test_cli_integration.py`)
- [ ] T015 [US1] Update `specs/001-cli-task-manager/quickstart.md` with an `add` example showing expected output

**Checkpoint**: User Story 1 should be fully functional and testable independently

## Phase 4: User Story 2 - Delete Task (Priority: P1)

**Goal**: Allow users to delete a task by id

**Independent Test**: Add a task, delete it via `python -m taskcli delete <id>`, then `list` should not include it

### Tests for User Story 2
- [ ] T016 [US2] Create unit test: verify `delete_task(id)` returns True for an existing id and False for missing id (file: `tasks/tasks5/tests/test_store.py`)

### Implementation for User Story 2
- [ ] T017 [US2] Implement `delete_task(task_id)` in `tasks/tasks5/src/taskcli/store.py` (safe mutation without corrupting storage)
- [ ] T018 [US2] Implement CLI `delete` subcommand in `tasks/tasks5/src/taskcli/cli.py` to call `delete_task` and print confirmation or error (exit code mapping: 0 success, 2 not found)
- [X] T019 [US2] Add integration test covering successful delete and delete-not-found behavior (file: `tasks/tasks5/tests/test_cli_delete_integration.py`)

**Checkpoint**: User Story 2 independently testable

## Phase 5: User Story 3 - List Tasks (Priority: P1)

**Goal**: List stored tasks in human-readable and JSON formats

**Independent Test**: Add multiple tasks then run `python -m taskcli list` and verify output lines (or `--format json` returns JSON array)

### Tests for User Story 3
- [X] T020 [US3] Create unit or CLI test: verify `list_tasks()` returns all tasks in insertion order and `--format json` returns valid JSON (file: `tasks/tasks5/tests/test_cli_list_integration.py`)

### Implementation for User Story 3
- [ ] T021 [US3] Implement `list` CLI output formatting (human + `--format json`) in `tasks/tasks5/src/taskcli/cli.py`
- [ ] T022 [US3] Ensure `list` prints `No tasks found.` when empty (CLI) and returns exit code 0
- [ ] T023 [US3] Add performance smoke test for listing 1,000 tasks (script: `tasks/tasks5/tests/perf/test_list_1000.py` - optional)

**Checkpoint**: User Stories 1-3 together form the MVP

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T024 [P] Add README examples and update `quickstart.md` with full examples for add/delete/list (file: `tasks/tasks5/quickstart.md`)
- [ ] T025 [P] Add CI coverage reporting and badge (workflow: `.github/workflows/ci.yml`, README badge: `tasks/tasks5/README.md`)
- [ ] T026 [P] Add deterministic error messages for all error cases and document them in `specs/001-cli-task-manager/contracts/cli-contract.md`
- [ ] T027 [P] Add environment variable override documentation for `TASKCLI_DATA` in `tasks/tasks5/README.md` and `specs/001-cli-task-manager/quickstart.md`
- [ ] T028 [P] Add packaging notes (optional): create `pyproject.toml` or `setup.cfg` if making distributable CLI (file: `pyproject.toml` at repo root)

## Dependencies & Execution Order

- **Setup (Phase 1)**: T001-T005 - can start immediately
- **Foundational (Phase 2)**: T006-T010 - blocks all user stories
- **User Stories**: T011-T023 - depend on Phase 2 completion
- **Polish (Final Phase)**: T024-T028 - depends on user stories

## Parallel Opportunities

- Tasks marked `[P]` can run in parallel (T002, T004, T007, T009, T025-T028)
- Unit test development tasks can be parallelized with implementation tasks in separate files
- Integration/perf tests can run in parallel once foundation tasks complete

## Task Counts & Summary

- Total tasks: 28
- Tasks per user story:
  - US1 (Add Task): 5 (T011-T015)
  - US2 (Delete Task): 4 (T016-T019)
  - US3 (List Task): 4 (T020-T023)
- Setup + Foundational + Polish: 15 tasks (T001-T010, T024-T028)

## Independent test criteria (one per story)

- US1: `python -m taskcli add "Title"` then `python -m taskcli list` shows the new task and returns exit code 0
- US2: `python -m taskcli delete <id>` removes task and returns exit code 0; deleting missing id returns exit code 2
- US3: `python -m taskcli list` returns human-readable lines; `python -m taskcli list --format json` returns JSON array

## Suggested MVP scope

- Implement only Phase 1 + Phase 2 + Phase 3 (User Story 1). That delivers core visible value (add+persist+list) and can be demoed.

## Validation

- Format validation: All tasks use the required checklist format `- [ ] Txxx [P?] [US?] Description` and include file paths where applicable.


*Generated by /speckit.tasks using plan.md and spec.md.*
