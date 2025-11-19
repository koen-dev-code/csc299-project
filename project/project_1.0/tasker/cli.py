"""Typer CLI for managing tasks stored in Neo4j."""
from __future__ import annotations

from typing import Optional, List
import os
import typer
from dotenv import load_dotenv

from .db import TaskDB

load_dotenv()

app = typer.Typer(help="Tasker CLI using Neo4j")


def _get_db() -> TaskDB:
    """Create a TaskDB using environment variables. Exits on missing config."""
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER")
    password = os.getenv("NEO4J_PASSWORD")
    if not (uri and user and password):
        typer.echo("Missing NEO4J_URI / NEO4J_USER / NEO4J_PASSWORD environment variables. See `.env.example`.")
        raise typer.Exit(code=1)
    return TaskDB(uri, user, password)


def _resolve_task_id(identifier: str, db: TaskDB) -> str:
    """Resolve a user-supplied identifier to a full task id.

    Allowed forms:
    - numeric index as shown by `list` (1-based)
    - short prefix of the UUID (must be unique)
    - full UUID
    """
    # numeric index
    if identifier.isdigit():
        idx = int(identifier) - 1
        items = db.list_tasks()
        if idx < 0 or idx >= len(items):
            typer.echo(f"Index out of range: {identifier}")
            raise typer.Exit(code=2)
        return items[idx]["id"]

    # try unique prefix match (common case)
    items = db.list_tasks()
    matches = [t for t in items if t.get("id", "").startswith(identifier)]
    if len(matches) == 1:
        return matches[0]["id"]
    if len(matches) > 1:
        typer.echo(f"Ambiguous id prefix: {identifier} matches multiple tasks")
        raise typer.Exit(code=2)

    # fallback: assume full id
    for t in items:
        if t.get("id") == identifier:
            return identifier

    typer.echo(f"Task not found: {identifier}")
    raise typer.Exit(code=2)


@app.command()
def add(
    title: str = typer.Argument(..., help="Title of the task"),
    description: Optional[str] = typer.Option(None, "-d", "--description", help="Optional task description"),
    tags: Optional[List[str]] = typer.Option(None, "-t", "--tag", help="Tag(s) for the task; pass multiple times"),
) -> None:
    """Add a new task."""
    db = _get_db()
    try:
        tag_list = list(tags) if tags else []
        task = db.create_task(title, description or "", tags=tag_list)
        typer.echo(f"Created task {task.get('id')}: {task.get('title')}")
    finally:
        db.close()


@app.command("list")
def list_tasks(
    status: str = typer.Option("all", "-s", "--status", help="Filter tasks: all|done|todo"),
    tag: Optional[str] = typer.Option(None, "-t", "--tag", help="Filter tasks by a tag"),
) -> None:
    """List tasks (all, done, or todo)."""
    db = _get_db()
    try:
        only_done = None
        if status == "done":
            only_done = True
        elif status == "todo":
            only_done = False

        items = db.list_tasks(only_done=only_done, tag=tag)
        if not items:
            typer.echo("No tasks found.")
            return
        for i, t in enumerate(items, start=1):
            mark = "✓" if t.get("done") else " "
            desc = t.get("description") or ""
            short = t.get("id", "")[:8]
            tags_out = ",".join(t.get("tags", [])) if t.get("tags") else ""
            tag_display = f" [{tags_out}]" if tags_out else ""
            typer.echo(f"{i:2d}. {short} [{mark}] {t.get('title')}{tag_display} - {desc}")
    finally:
        db.close()


@app.command()
def complete(task_id: str = typer.Argument(..., help="ID of the task to mark done")) -> None:
    """Mark a task as completed."""
    db = _get_db()
    try:
        full_id = _resolve_task_id(task_id, db)
        updated = db.complete_task(full_id)
        if not updated:
            typer.echo("Task not found.")
            raise typer.Exit(code=2)
        typer.echo(f"Marked done: {updated.get('id')} - {updated.get('title')}")
    finally:
        db.close()


@app.command()
def delete(task_id: str = typer.Argument(..., help="ID of the task to delete")) -> None:
    """Delete a task by id."""
    db = _get_db()
    try:
        full_id = _resolve_task_id(task_id, db)
        db.delete_task(full_id)
        typer.echo(f"Deleted task {full_id}")
    finally:
        db.close()
