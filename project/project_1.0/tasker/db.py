"""Neo4j database helper for Tasker.

Provides a small `TaskDB` class wrapping the neo4j driver for simple CRUD.
"""
from __future__ import annotations

from typing import Dict, List, Optional
import uuid
from neo4j import GraphDatabase, Driver


class TaskDB:
    """Simple wrapper around a Neo4j driver for Task nodes.

    Each task node has properties: `id`, `title`, `description`, `done`, `created`.
    """

    def __init__(self, uri: str, user: str, password: str):
        self._driver: Driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self) -> None:
        """Close the underlying Neo4j driver."""
        self._driver.close()

    def create_task(self, title: str, description: str = "") -> Dict:
        """Create a new task and return its properties."""
        task_id = str(uuid.uuid4())
        query = (
            "CREATE (t:Task {id:$id, title:$title, description:$description, done:false, created:datetime()}) "
            "RETURN t"
        )
        with self._driver.session() as session:
            rec = session.run(query, id=task_id, title=title, description=description).single()
            node = rec["t"]
            props = dict(node)
            return props

    def list_tasks(self, only_done: Optional[bool] = None) -> List[Dict]:
        """List tasks. If `only_done` is True/False filter by `done`, otherwise return all."""
        if only_done is None:
            query = "MATCH (t:Task) RETURN t ORDER BY t.created DESC"
            params = {}
        else:
            query = "MATCH (t:Task {done:$done}) RETURN t ORDER BY t.created DESC"
            params = {"done": only_done}
        tasks: List[Dict] = []
        with self._driver.session() as session:
            result = session.run(query, **params)
            for r in result:
                node = r["t"]
                props = dict(node)
                # Ensure created is JSON-serializable string
                if "created" in props:
                    props["created"] = str(props["created"])
                tasks.append(props)
        return tasks

    def complete_task(self, task_id: str) -> Optional[Dict]:
        """Mark a task done and return the updated properties, or None if not found."""
        query = "MATCH (t:Task {id:$id}) SET t.done = true RETURN t"
        with self._driver.session() as session:
            rec = session.run(query, id=task_id).single()
            if not rec:
                return None
            node = rec["t"]
            return dict(node)

    def delete_task(self, task_id: str) -> bool:
        """Delete a task by id; returns True (always) for now."""
        query = "MATCH (t:Task {id:$id}) DETACH DELETE t"
        with self._driver.session() as session:
            session.run(query, id=task_id)
        return True
