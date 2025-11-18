import json
import os
import tempfile
from typing import List, Optional
from .models import Task, now_iso


class JSONStorage:
    def __init__(self, path: Optional[str] = None):
        # Default path: environment variable TASKS_DB or file in current working directory
        if path:
            self.path = path
        else:
            self.path = os.environ.get("TASKS_DB") or os.path.join(os.getcwd(), "tasks.json")

    def _ensure_parent(self):
        parent = os.path.dirname(self.path)
        if parent and not os.path.exists(parent):
            os.makedirs(parent, exist_ok=True)

    def load(self) -> List[Task]:
        if not os.path.exists(self.path):
            return []
        with open(self.path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                return []
        tasks = [Task.from_dict(t) for t in data.get("tasks", [])]
        return tasks

    def save(self, tasks: List[Task]):
        self._ensure_parent()
        data = {"tasks": [t.to_dict() for t in tasks]}
        dir_name = os.path.dirname(self.path) or "."
        fd, tmp_path = tempfile.mkstemp(prefix="tasks-", dir=dir_name)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, self.path)
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

    def add_task(self, task: Task):
        tasks = self.load()
        tasks.append(task)
        self.save(tasks)

    def update_task(self, task_id: str, **updates) -> Task:
        tasks = self.load()
        found = False
        for i, t in enumerate(tasks):
            if t.id == task_id:
                found = True
                # apply updates
                if "title" in updates and updates["title"] is not None:
                    if not updates["title"].strip():
                        raise ValueError("title must be non-empty")
                    t.title = updates["title"].strip()
                if "description" in updates:
                    t.description = updates.get("description")
                if "status" in updates:
                    t.status = updates.get("status")
                if "due_date" in updates:
                    t.due_date = updates.get("due_date")
                if "priority" in updates:
                    t.priority = updates.get("priority")
                t.updated_at = now_iso()
                tasks[i] = t
                break
        if not found:
            raise KeyError(f"task not found: {task_id}")
        self.save(tasks)
        return t

    def delete_task(self, task_id: str):
        tasks = self.load()
        new = [t for t in tasks if t.id != task_id]
        if len(new) == len(tasks):
            raise KeyError(f"task not found: {task_id}")
        self.save(new)

    def list_tasks(self, status: Optional[str] = None, q: Optional[str] = None) -> List[Task]:
        tasks = self.load()
        if status:
            tasks = [t for t in tasks if t.status == status]
        if q:
            ql = q.lower()
            tasks = [t for t in tasks if ql in (t.title or "").lower() or ql in (t.description or "").lower()]
        return tasks

    def get(self, task_id: str) -> Task:
        tasks = self.load()
        for t in tasks:
            if t.id == task_id:
                return t
        raise KeyError(f"task not found: {task_id}")
