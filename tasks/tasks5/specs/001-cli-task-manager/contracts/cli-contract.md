# Contracts: CLI Task Management

**Feature**: CLI Task Management (`001-cli-task-manager`)  
**Date**: 2025-11-12

This document describes the user-facing CLI contract: commands, arguments, outputs,
and exit codes. It's intentionally implementation-agnostic.

## Commands

### add
Purpose: Create a new task.

Usage: `taskcli add "TITLE" [--description "TEXT"]`

Behavior:
- On success: prints the new task's identifier and a brief confirmation message to stdout, and exits with code 0.
- On validation error (e.g., empty title): prints an explanatory message to stderr and exits with a non-zero code.

Output (stdout): `<id>` (newline) `Added task: TITLE`

### delete
Purpose: Delete a task by id.

Usage: `taskcli delete <id>`

Behavior:
- On success: prints confirmation to stdout and exits with code 0.
- If id not found: prints an explanatory message to stderr and exits with a non-zero code.

Output (stdout): `Deleted task <id>`

### list
Purpose: List tasks.

Usage: `taskcli list`

Behavior:
- On success: prints one line per task with `id  title` (or JSON output if `--format json` is specified).
- If no tasks: prints `No tasks found.` and exits with code 0.

Output default (human):
`<id>  <title>`

Optional flags:
- `--format json` : prints a JSON array of task objects to stdout (machine-consumable)

## Exit Codes
- 0: success
- 1: general error / invalid usage
- 2: not found (e.g., delete non-existent id)

## Error messages
Error messages must be deterministic and suitable for automated tests (avoid including
timestamps or non-deterministic data in error strings).
