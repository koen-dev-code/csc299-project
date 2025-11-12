"""Simple JSON-backed task store for the CLI task manager.

API (functions):
- add_task(title, description=None, data_path=None) -> id
- delete_task(task_id, data_path=None) -> bool
- list_tasks(data_path=None) -> list[dict]

The data file is a JSON object with a "tasks" list. Writes are atomic using
write-then-rename pattern.
"""
from __future__ import annotations
import json
import os
import tempfile
import uuid
from datetime import datetime
from typing import List, Dict, Optional

def _get_default_data_path() -> str:
    """Return the default data path, checking TASKCLI_DATA at call time.

    Computing this at call time avoids import-time caching so tests that set
    the environment can control where data is written.
    """
    return os.environ.get('TASKCLI_DATA') or os.path.join(os.path.expanduser('~'), '.taskcli_tasks.json')


def _read_data(path: str) -> Dict:
    if not os.path.exists(path):
        return {"tasks": []}
    with open(path, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            # Corrupted file — treat as empty to avoid crashes; caller may handle
            return {"tasks": []}


def _write_data_atomic(path: str, data: Dict) -> None:
    dirpath = os.path.dirname(path) or '.'
    fd, tmp = tempfile.mkstemp(dir=dirpath, prefix='.tmp-taskcli-')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except Exception:
                pass


def add_task(title: str, description: Optional[str] = None, data_path: Optional[str] = None) -> str:
    if not title or not title.strip():
        raise ValueError('title must be non-empty')
    path = data_path or _get_default_data_path()
    data = _read_data(path)
    task_id = str(uuid.uuid4())
    task = {
        'id': task_id,
        'title': title.strip(),
        'description': description or '',
        'created_at': datetime.utcnow().replace(microsecond=0).isoformat() + 'Z',
        'completed': False,
    }
    data.setdefault('tasks', []).append(task)
    _write_data_atomic(path, data)
    return task_id


def delete_task(task_id: str, data_path: Optional[str] = None) -> bool:
    path = data_path or _get_default_data_path()
    data = _read_data(path)
    tasks = data.get('tasks', [])
    new_tasks = [t for t in tasks if t.get('id') != task_id]
    if len(new_tasks) == len(tasks):
        return False
    data['tasks'] = new_tasks
    _write_data_atomic(path, data)
    return True


def list_tasks(data_path: Optional[str] = None) -> List[Dict]:
    path = data_path or _get_default_data_path()
    data = _read_data(path)
    return data.get('tasks', [])
