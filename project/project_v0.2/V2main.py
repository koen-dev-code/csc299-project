import argparse
import sys
from typing import List

from V2database import TaskManager


def parse_tags(tags_str: str) -> List[str]:
    if not tags_str:
        return []
    return [t.strip() for t in tags_str.split(",") if t.strip()]


def cmd_add(args, tm: TaskManager):
    tags = parse_tags(args.tags or "")
    task = tm.add_task(args.title, description=(args.description or ""), tags=tags)
    print(f"Added task {task['id']}: {task['title']}")


def cmd_remove(args, tm: TaskManager):
    try:
        tid = int(args.id)
    except ValueError:
        print("Task id must be an integer")
        return
    ok = tm.remove_task(tid)
    if ok:
        print(f"Removed task {tid}")
    else:
        print(f"Task {tid} not found")


def cmd_list(args, tm: TaskManager):
    tasks = tm.list_tasks(tag=args.tag)
    if not tasks:
        print("No tasks found")
        return
    for t in tasks:
        tags = ",".join(t.get("tags", []))
        print(f"[{t['id']}] {t['title']} (tags: {tags})")
        if args.verbose:
            desc = t.get("description", "")
            print("    ", desc)


def cmd_show(args, tm: TaskManager):
    try:
        tid = int(args.id)
    except ValueError:
        print("Task id must be an integer")
        return
    t = tm.get_task(tid)
    if not t:
        print(f"Task {tid} not found")
        return
    print(f"ID: {t['id']}")
    print(f"Title: {t['title']}")
    print(f"Description: {t.get('description','')}")
    print(f"Tags: {','.join(t.get('tags',[]))}")
    print(f"Created: {t.get('created_at')}")


def cmd_update(args, tm: TaskManager):
    try:
        tid = int(args.id)
    except ValueError:
        print("Task id must be an integer")
        return
    tags = None if args.tags is None else parse_tags(args.tags)
    updated = tm.update_task(tid, title=args.title, description=args.description, tags=tags)
    if not updated:
        print(f"Task {tid} not found")
    else:
        print(f"Updated task {tid}")


def interactive(tm: TaskManager):
    print("Entering interactive mode. Commands: add, list, show, remove, update, quit")
    while True:
        try:
            line = input("> ").strip()
        except EOFError:
            break
        if not line:
            continue
        parts = line.split()
        cmd = parts[0].lower()
        rest = parts[1:]
        if cmd in ("q", "quit", "exit"):
            break
        if cmd == "add":
            # simple: add <title> --desc "desc" --tags a,b
            title = " ".join(rest) or "Untitled"
            tm.add_task(title)
            print("Added (simple) task")
        elif cmd == "list":
            tasks = tm.list_tasks()
            for t in tasks:
                print(f"[{t['id']}] {t['title']} ({','.join(t.get('tags',[]))})")
        elif cmd == "remove" and rest:
            try:
                tid = int(rest[0])
                tm.remove_task(tid)
                print(f"Removed {tid}")
            except Exception:
                print("Usage: remove <id>")
        elif cmd == "show" and rest:
            try:
                tid = int(rest[0])
                t = tm.get_task(tid)
                if t:
                    print(t)
                else:
                    print("Not found")
            except Exception:
                print("Usage: show <id>")
        elif cmd == "update" and rest:
            try:
                tid = int(rest[0])
                # naive: everything after id becomes title
                title = " ".join(rest[1:]) or None
                tm.update_task(tid, title=title)
                print("Updated")
            except Exception:
                print("Usage: update <id> <new title>")
        else:
            print("Unknown command")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Task manager (v2) - add/remove tasks with tags and descriptions")
    sub = parser.add_subparsers(dest="cmd")

    a_add = sub.add_parser("add", help="Add a task")
    a_add.add_argument("title", help="Task title")
    a_add.add_argument("-d", "--description", help="Task description")
    a_add.add_argument("-t", "--tags", help="Comma-separated tags")
    a_add.set_defaults(func=cmd_add)

    a_remove = sub.add_parser("remove", help="Remove a task by id")
    a_remove.add_argument("id", help="Task id")
    a_remove.set_defaults(func=cmd_remove)

    a_list = sub.add_parser("list", help="List tasks")
    a_list.add_argument("--tag", help="Filter by tag")
    a_list.add_argument("-v", "--verbose", action="store_true", help="Show descriptions")
    a_list.set_defaults(func=cmd_list)

    a_show = sub.add_parser("show", help="Show a task by id")
    a_show.add_argument("id", help="Task id")
    a_show.set_defaults(func=cmd_show)

    a_update = sub.add_parser("update", help="Update a task (title, description, tags)")
    a_update.add_argument("id", help="Task id")
    a_update.add_argument("--title", help="New title")
    a_update.add_argument("--description", help="New description")
    a_update.add_argument("--tags", help="Comma-separated tags (use empty string to clear)")
    a_update.set_defaults(func=cmd_update)

    args = parser.parse_args(argv)
    tm = TaskManager()

    if not args.cmd:
        interactive(tm)
        return

    # call the selected command handler
    if hasattr(args, "func"):
        args.func(args, tm)


if __name__ == "__main__":
    main()