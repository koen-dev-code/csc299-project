import argparse
import os
from typing import Optional

from .models import Task
from .storage import JSONStorage


def get_storage(path: "Optional[str]" = None) -> JSONStorage:
    from typing import Optional
    return JSONStorage(path=path)


def cmd_create(args):
    storage = get_storage(args.db)
    task = Task.create(title=args.title, description=args.description)
    storage.add_task(task)
    print(task.id)


def cmd_list(args):
    storage = get_storage(args.db)
    tasks = storage.list_tasks(status=args.status, q=args.q)
    for t in tasks:
        print(f"{t.id}  [{t.status}] {t.title}")


def cmd_complete(args):
    storage = get_storage(args.db)
    storage.update_task(args.id, status="completed")
    print(args.id)


def cmd_delete(args):
    storage = get_storage(args.db)
    storage.delete_task(args.id)
    print(args.id)


def cmd_edit(args):
    storage = get_storage(args.db)
    updates = {}
    if args.title is not None:
        updates["title"] = args.title
    if args.description is not None:
        updates["description"] = args.description
    storage.update_task(args.id, **updates)
    print(args.id)


def build_parser():
    p = argparse.ArgumentParser(prog="tasks-cli")
    p.add_argument("--db", help="path to tasks db file", default=os.environ.get("TASKS_DB"))
    sub = p.add_subparsers(dest="cmd")

    c_create = sub.add_parser("create")
    c_create.add_argument("--title", required=True)
    c_create.add_argument("--description")
    c_create.set_defaults(func=cmd_create)

    c_list = sub.add_parser("list")
    c_list.add_argument("--status", choices=["open", "completed"]) 
    c_list.add_argument("--q")
    c_list.set_defaults(func=cmd_list)

    c_complete = sub.add_parser("complete")
    c_complete.add_argument("--id", required=True)
    c_complete.set_defaults(func=cmd_complete)

    c_delete = sub.add_parser("delete")
    c_delete.add_argument("--id", required=True)
    c_delete.set_defaults(func=cmd_delete)

    c_edit = sub.add_parser("edit")
    c_edit.add_argument("--id", required=True)
    c_edit.add_argument("--title")
    c_edit.add_argument("--description")
    c_edit.set_defaults(func=cmd_edit)

    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return 1
    try:
        args.func(args)
    except Exception as e:
        print(f"Error: {e}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
