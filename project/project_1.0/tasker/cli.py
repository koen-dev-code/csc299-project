"""Typer CLI for managing tasks stored in Neo4j."""
from __future__ import annotations

from typing import Optional, List
import os
import typer
import json
import openai
import traceback
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


def suggest_tags_with_openai(title: str, description: str | None) -> List[str]:
    """Request tag suggestions from OpenAI and return a filtered list of allowed tags.

    Robustly handles both the new `openai.OpenAI` client and the older
    `openai.ChatCompletion.create` interface. The model is instructed to only
    return tags from the `allowed` list, but we defensively parse the result
    as JSON or a comma-separated list and fall back to extracting allowed
    words.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return []

    # try to set legacy API key if present; new client ignores this
    try:
        openai.api_key = api_key
    except Exception:
        pass

    allowed = ["store", "home", "work", "urgent", "later", "errands", "finance", "personal", "health"]

    system_msg = (
        "You are a helpful assistant that recommends zero or more tags for a task."
        " Only choose tags from the allowed list and return them in a simple format (preferably a JSON array, e.g. [\"home\",\"store\"])."
    )
    user_msg = (
        "Allowed tags: " + ", ".join(allowed) + "\n\n"
        + "Task title: "
        + title
        + "\nTask description: "
        + (description or "")
        + "\n\nReturn only a JSON array of selected tags from the allowed list, or an empty array [] if none."
    )

    content = ""
    try:
        OpenAIClient = getattr(openai, "OpenAI", None)
        if OpenAIClient is not None:
            client = OpenAIClient()
            resp = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": user_msg}],
                max_tokens=80,
                temperature=0.0,
            )
            # new client: resp.choices[0].message.content
            content = getattr(getattr(resp.choices[0], "message", None), "content", "") or ""
        else:
            resp = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": user_msg}],
                max_tokens=80,
                temperature=0.0,
            )
            content = resp["choices"][0]["message"]["content"].strip()
    except Exception:
        return []

    content = content.strip()
    if not content:
        return []

    # 1) Try parsing as JSON array
    try:
        parsed = json.loads(content)
        if isinstance(parsed, list):
            seen = set()
            out = []
            for t in parsed:
                if isinstance(t, str):
                    key = t.strip().lower()
                    if key in allowed and key not in seen:
                        seen.add(key)
                        out.append(key)
            return out
    except Exception:
        pass

    # 2) If content contains a JSON-like substring, try to extract first bracketed array
    start = content.find("[")
    end = content.rfind("]")
    if start != -1 and end != -1 and end > start:
        try:
            parsed = json.loads(content[start : end + 1])
            if isinstance(parsed, list):
                seen = set()
                out = []
                for t in parsed:
                    if isinstance(t, str):
                        key = t.strip().lower()
                        if key in allowed and key not in seen:
                            seen.add(key)
                            out.append(key)
                return out
        except Exception:
            pass

    # 3) Otherwise, split on commas or whitespace and filter allowed words
    tokens = [tok.strip().lower().strip(".,") for tok in content.replace("\n", ",").split(",") if tok.strip()]
    seen = set()
    out = []
    for tok in tokens:
        # tok may be a phrase; check if any allowed word is contained
        for a in allowed:
            if tok == a or tok.startswith(a + " ") or (" " + a) in tok or tok.endswith(" " + a):
                if a not in seen:
                    seen.add(a)
                    out.append(a)
    # final fallback: find any allowed words in the content
    if not out:
        for a in allowed:
            if a in content.lower().split():
                if a not in seen:
                    seen.add(a)
                    out.append(a)

    return out


@app.command()
def check() -> None:
    """Run health checks for Neo4j and OpenAI (if configured)."""
    ok = True

    # Check Neo4j
    typer.echo("Checking Neo4j...")
    try:
        db = _get_db()
        try:
            with db._driver.session() as session:
                r = session.run("RETURN 1 AS v")
                row = r.single()
                if row and row.get("v") == 1:
                    typer.secho("  Neo4j: OK", fg=typer.colors.GREEN)
                else:
                    typer.secho("  Neo4j: unexpected result", fg=typer.colors.YELLOW)
                    ok = False
        finally:
            db.close()
    except Exception:
        typer.secho("  Neo4j: FAILED", fg=typer.colors.RED)
        traceback.print_exc()
        ok = False

    # Check OpenAI
    typer.echo("Checking OpenAI...")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        typer.secho("  OpenAI: not configured (OPENAI_API_KEY missing)", fg=typer.colors.YELLOW)
        ok = ok and True
    else:
        try:
            # Prefer new client
            OpenAIClient = getattr(openai, "OpenAI", None)
            if OpenAIClient is not None:
                client = OpenAIClient()
                resp = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "Respond with a single word: pong"}],
                    max_tokens=10,
                    temperature=0.0,
                )
                content = resp.choices[0].message.content.strip()
            else:
                resp = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "Respond with a single word: pong"}],
                    max_tokens=10,
                    temperature=0.0,
                )
                content = resp["choices"][0]["message"]["content"].strip()
            typer.secho(f"  OpenAI: OK (response: {content})", fg=typer.colors.GREEN)
        except Exception:
            typer.secho("  OpenAI: FAILED", fg=typer.colors.RED)
            traceback.print_exc()
            ok = False

    if not ok:
        raise typer.Exit(code=2)


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
    suggest: bool = typer.Option(False, "--suggest", help="Use OpenAI to suggest tags for this task (requires OPENAI_API_KEY)"),
) -> None:
    """Add a new task."""
    db = _get_db()
    try:
        tag_list = list(tags) if tags else []
        task = db.create_task(title, description or "", tags=tag_list)
        typer.echo(f"Created task {task.get('id')}: {task.get('title')}")

        # Optionally ask OpenAI for tag suggestions and apply them
        if suggest:
            suggested = suggest_tags_with_openai(title, description)
            if suggested:
                # Merge unique tags with any provided tags
                merged = list(dict.fromkeys((tag_list or []) + suggested))
                try:
                    with db._driver.session() as session:
                        session.run(
                            "MATCH (t:Task {id:$id}) SET t.tags = $tags RETURN t",
                            id=task.get("id"),
                            tags=merged,
                        )
                    typer.echo(f"Added suggested tags: {', '.join(suggested)}")
                except Exception:
                    typer.echo("Warning: failed to persist suggested tags")
            else:
                typer.echo("No tag suggestions from the AI.")
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
