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


@app.command()
def add(title: str = typer.Argument(..., help="Title of the task"), description: Optional[str] = typer.Option(None, "-d", "--description", help="Optional task description")) -> None:
    """Add a new task."""
    db = _get_db()
    try:
        task = db.create_task(title, description or "")
        typer.echo(f"Created task {task.get('id')}: {task.get('title')}")
    finally:
        db.close()


@app.command("list")
def list_tasks(status: str = typer.Option("all", "-s", "--status", help="Filter tasks: all|done|todo")) -> None:
    """List tasks (all, done, or todo)."""
    db = _get_db()
    try:
        if status == "done":
            items = db.list_tasks(only_done=True)
        elif status == "todo":
            items = db.list_tasks(only_done=False)
        else:
            items = db.list_tasks()
        if not items:
            typer.echo("No tasks found.")
            return
        for t in items:
            mark = "✓" if t.get("done") else " "
            desc = t.get("description") or ""
            typer.echo(f"{t.get('id')} [{mark}] {t.get('title')} - {desc}")
    finally:
        db.close()


@app.command()
def complete(task_id: str = typer.Argument(..., help="ID of the task to mark done")) -> None:
    """Mark a task as completed."""
    db = _get_db()
    try:
        updated = db.complete_task(task_id)
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
        db.delete_task(task_id)
        typer.echo(f"Deleted task {task_id}")
    finally:
        db.close()
