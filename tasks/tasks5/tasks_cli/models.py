from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional
import uuid


def now_iso():
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


@dataclass
class Task:
    id: str
    title: str
    description: Optional[str]
    status: str
    created_at: str
    updated_at: Optional[str]
    due_date: Optional[str]
    priority: Optional[str]

    @staticmethod
    def create(title: str, description: Optional[str] = None, due_date: Optional[str] = None, priority: Optional[str] = None):
        if not title or not title.strip():
            raise ValueError("title must be a non-empty string")
        tid = str(uuid.uuid4())
        now = now_iso()
        return Task(
            id=tid,
            title=title.strip(),
            description=description,
            status="open",
            created_at=now,
            updated_at=None,
            due_date=due_date,
            priority=priority,
        )

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "Task":
        return Task(
            id=d["id"],
            title=d.get("title", ""),
            description=d.get("description"),
            status=d.get("status", "open"),
            created_at=d.get("created_at", now_iso()),
            updated_at=d.get("updated_at"),
            due_date=d.get("due_date"),
            priority=d.get("priority"),
        )
