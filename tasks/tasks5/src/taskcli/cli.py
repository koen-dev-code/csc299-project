"""CLI entrypoints using argparse for the taskcli package."""
from __future__ import annotations
import argparse
import json
import sys
from typing import Optional

from .store import add_task, delete_task, list_tasks


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog='taskcli', description='Simple task CLI')
    sub = parser.add_subparsers(dest='cmd')

    p_add = sub.add_parser('add', help='Add a task')
    p_add.add_argument('title', help='Task title')
    p_add.add_argument('--description', '-d', help='Optional description', default='')

    p_delete = sub.add_parser('delete', help='Delete a task')
    p_delete.add_argument('id', help='Task id')

    p_list = sub.add_parser('list', help='List tasks')
    p_list.add_argument('--format', choices=['human', 'json'], default='human')

    args = parser.parse_args(argv)

    if args.cmd == 'add':
        try:
            tid = add_task(args.title, args.description)
            print(tid)
            print(f"Added task: {args.title}")
            return 0
        except ValueError as e:
            print(str(e), file=sys.stderr)
            return 1
    elif args.cmd == 'delete':
        ok = delete_task(args.id)
        if ok:
            print(f"Deleted task {args.id}")
            return 0
        else:
            print(f"Task not found: {args.id}", file=sys.stderr)
            return 2
    elif args.cmd == 'list':
        tasks = list_tasks()
        if not tasks:
            print('No tasks found.')
            return 0
        if args.format == 'json':
            print(json.dumps(tasks, ensure_ascii=False))
            return 0
        for t in tasks:
            print(f"{t.get('id')}  {t.get('title')}")
        return 0
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
