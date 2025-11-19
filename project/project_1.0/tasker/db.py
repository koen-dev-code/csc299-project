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

    def create_task(self, title: str, description: str = "", tags: Optional[List[str]] = None) -> Dict:
        """Create a new task and return its properties."""
        task_id = str(uuid.uuid4())
        query = (
            "CREATE (t:Task {id:$id, title:$title, description:$description, done:false, tags:$tags, created:datetime()}) "
            "RETURN t"
        )
        tags_list = tags or []
        with self._driver.session() as session:
            rec = session.run(query, id=task_id, title=title, description=description, tags=tags_list).single()
            node = rec["t"]
            props = dict(node)
            return props

    def list_tasks(self, only_done: Optional[bool] = None, tag: Optional[str] = None) -> List[Dict]:
        """List tasks.

        If `only_done` is True/False filter by `done`, otherwise return all.
        If `tag` is provided, only return tasks that include the tag in their `tags` list.
        """
        params = {}
        where_clauses: list[str] = []
        if only_done is not None:
            where_clauses.append("t.done = $done")
            params["done"] = only_done
        if tag:
            where_clauses.append("$tag IN t.tags")
            params["tag"] = tag

        where = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
        query = f"MATCH (t:Task) {where} RETURN t ORDER BY t.created DESC"
        tasks: List[Dict] = []
        with self._driver.session() as session:
            result = session.run(query, **params)
            for r in result:
                node = r["t"]
                props = dict(node)
                # Ensure created is JSON-serializable string
                if "created" in props:
                    props["created"] = str(props["created"])
                # Ensure tags is a plain list
                if "tags" in props and props["tags"] is None:
                    props["tags"] = []
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

    def delete_all_tasks(self) -> int:
        """Delete all Task nodes and return the number deleted."""
        with self._driver.session() as session:
            rec = session.run("MATCH (t:Task) RETURN count(t) AS c").single()
            count = int(rec["c"]) if rec and rec["c"] is not None else 0
            if count:
                session.run("MATCH (t:Task) DETACH DELETE t")
            return count

    def delete_completed_tasks(self) -> int:
        """Delete all tasks where `done` is true and return the number deleted."""
        with self._driver.session() as session:
            rec = session.run("MATCH (t:Task {done:true}) RETURN count(t) AS c").single()
            count = int(rec["c"]) if rec and rec["c"] is not None else 0
            if count:
                session.run("MATCH (t:Task {done:true}) DETACH DELETE t")
            return count
