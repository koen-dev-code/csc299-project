import argparse
import json
import os
import sys
from datetime import datetime

# Usage examples:
#   python task.py add "Buy milk" -d "2 liters" -t groceries,errands
#   python task.py list
#   python task.py list --pending
#   python task.py search -q milk
#   python task.py search --tag groceries
#   python task.py complete 1
#
# Commands:
#   add       Add a new task (title required, optional --desc, --tags comma-separated)
#   list      List tasks (use --pending to show only incomplete tasks)
#   search    Search tasks by text (--query/-q) or by tag (--tag)
#   complete  Mark a task complete by id

DATA_FILE = os.path.join(os.path.dirname(__file__), "tasks.json")


def load_tasks():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_tasks(tasks):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)


def next_id(tasks):
    if not tasks:
        return 1
    return max(t.get("id", 0) for t in tasks) + 1


def add_task(title, description=None, tags=None):
    tasks = load_tasks()
    task = {
        "id": next_id(tasks),
        "title": title,
        "description": description or "",
        "tags": tags or [],
        "completed": False,
        "created": datetime.utcnow().isoformat() + "Z",
    }
    tasks.append(task)
    save_tasks(tasks)
    print(f"Added task {task['id']}: {task['title']}")


def list_tasks(show_all=True):
    tasks = load_tasks()
    if not show_all:
        tasks = [t for t in tasks if not t.get("completed", False)]
    if not tasks:
        print("No tasks found.")
        return
    for t in sorted(tasks, key=lambda x: (x.get("completed", False), x.get("created")), reverse=False):
        status = "✓" if t.get("completed") else " "
        tags = ", ".join(t.get("tags", []))
        print(f"[{status}] {t['id']}: {t['title']}")
        if t.get("description"):
            print(f"    {t['description']}")
        if tags:
            print(f"    tags: {tags}")


def search_tasks(query=None, tag=None):
    tasks = load_tasks()
    if not tasks:
        print("No tasks found.")
        return
    results = []
    if tag:
        for t in tasks:
            if tag in t.get("tags", []):
                results.append(t)
    elif query:
        q = query.lower()
        for t in tasks:
            if q in t.get("title", "").lower() or q in t.get("description", "").lower():
                results.append(t)
    else:
        print("Provide --query or --tag to search.")
        return

    if not results:
        print("No matching tasks.")
        return

    for t in results:
        status = "✓" if t.get("completed") else " "
        tags = ", ".join(t.get("tags", []))
        print(f"[{status}] {t['id']}: {t['title']}")
        if t.get("description"):
            print(f"    {t['description']}")
        if tags:
            print(f"    tags: {tags}")


def mark_complete(task_id):
    tasks = load_tasks()
    for t in tasks:
        if t.get("id") == task_id:
            if t.get("completed"):
                print(f"Task {task_id} is already completed.")
            else:
                t["completed"] = True
                save_tasks(tasks)
                print(f"Marked task {task_id} as complete.")
            return
    print(f"Task {task_id} not found.")


def parse_args(argv):
    # Provide example usage in the help output; use RawDescriptionHelpFormatter
    epilog = """Examples:
  task1 add "Buy milk" -d "2 liters" -t groceries,errands
  task1 list
  task1 list --pending
  task1 search -q milk
  task1 search --tag groceries
  task1 complete 1
"""
    p = argparse.ArgumentParser(
        prog="task1",
        description="Task manager (JSON-backed)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=epilog,
    )
    sub = p.add_subparsers(dest="cmd")

    # add: create a task. Example: task1 add "Title" -d "desc" -t tag1,tag2
    a_add = sub.add_parser("add", help="Add a new task")
    a_add.add_argument("title", help="Title of the task")
    a_add.add_argument("--desc", "-d", help="Description", default="")
    a_add.add_argument("--tags", "-t", help="Comma-separated tags", default="")

    # list: show tasks. Use --pending to list only incomplete tasks.
    a_list = sub.add_parser("list", help="List tasks")
    a_list.add_argument("--pending", action="store_true", help="Show only pending tasks")

    # search: find tasks by query text (-q) or by tag (--tag)
    a_search = sub.add_parser("search", help="Search tasks")
    a_search.add_argument("--query", "-q", help="Search text in title/description")
    a_search.add_argument("--tag", help="Search by tag")

    # complete: mark a task complete by its numeric id
    a_done = sub.add_parser("complete", help="Mark task complete")
    a_done.add_argument("id", type=int, help="Task id to mark complete")

    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv or sys.argv[1:])
    if args.cmd == "add":
        tags = [t.strip() for t in args.tags.split(",")] if args.tags else []
        tags = [t for t in tags if t]
        add_task(args.title, description=args.desc, tags=tags)
    elif args.cmd == "list":
        list_tasks(show_all=not args.pending)
    elif args.cmd == "search":
        search_tasks(query=args.query, tag=args.tag)
    elif args.cmd == "complete":
        mark_complete(args.id)
    else:
        print("No command provided. Use --help for usage.")


if __name__ == "__main__":
    main()
