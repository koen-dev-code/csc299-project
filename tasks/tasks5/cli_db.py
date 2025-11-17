#!/usr/bin/env python3
"""Simple CLI JSON-backed key-value store.

Usage examples:
  python cli_db.py add KEY VALUE
  python cli_db.py get KEY
  python cli_db.py list
  python cli_db.py delete KEY

Data is stored in a JSON file (default: .cli_db.json). Use --db to override.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any


def default_db_path() -> str:
    return os.path.join(os.path.dirname(__file__), ".cli_db.json")


def load_db(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # If file is corrupted, treat as empty but warn
        print(f"warning: could not read database file '{path}', starting fresh", file=sys.stderr)
        return {}


def save_db(path: str, data: Dict[str, Any]) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


def cmd_add(args: argparse.Namespace) -> int:
    db = load_db(args.db)
    key = args.key
    value = args.value
    db[key] = {"value": value, "updated_at": datetime.utcnow().isoformat() + "Z"}
    save_db(args.db, db)
    print(f"ok: set '{key}'")
    return 0


def cmd_get(args: argparse.Namespace) -> int:
    db = load_db(args.db)
    key = args.key
    if key not in db:
        print(f"error: key '{key}' not found", file=sys.stderr)
        return 2
    val = db[key]
    # If value is an object with metadata, print just the stored value
    if isinstance(val, dict) and "value" in val:
        print(val["value"])
    else:
        print(json.dumps(val, ensure_ascii=False))
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    db = load_db(args.db)
    for k, v in db.items():
        if isinstance(v, dict) and "value" in v:
            print(f"{k}: {v['value']}")
        else:
            print(f"{k}: {json.dumps(v, ensure_ascii=False)}")
    return 0


def cmd_delete(args: argparse.Namespace) -> int:
    db = load_db(args.db)
    key = args.key
    if key in db:
        del db[key]
        save_db(args.db, db)
        print(f"ok: deleted '{key}'")
        return 0
    else:
        print(f"error: key '{key}' not found", file=sys.stderr)
        return 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cli_db", description="Simple CLI JSON-backed key-value store")
    parser.add_argument("--db", default=default_db_path(), help="Path to JSON database file")
    sub = parser.add_subparsers(dest="cmd")

    p_add = sub.add_parser("add", help="Add or update a key")
    p_add.add_argument("key")
    p_add.add_argument("value")
    p_add.set_defaults(func=cmd_add)

    p_get = sub.add_parser("get", help="Get value for key")
    p_get.add_argument("key")
    p_get.set_defaults(func=cmd_get)

    p_list = sub.add_parser("list", help="List all keys")
    p_list.set_defaults(func=cmd_list)

    p_delete = sub.add_parser("delete", help="Delete a key")
    p_delete.add_argument("key")
    p_delete.set_defaults(func=cmd_delete)

    return parser


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return 1
    try:
        return args.func(args)
    except Exception as e:
        print(f"fatal: {e}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
