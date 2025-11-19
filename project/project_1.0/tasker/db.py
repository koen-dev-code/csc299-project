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
        tags_list = tags or []
        with self._driver.session() as session:
            # create task node
            session.run(
                "CREATE (t:Task {id:$id, title:$title, description:$description, done:false, created:datetime()})",
                id=task_id,
                title=title,
                description=description,
            )
            # create/attach tags as Tag nodes
            if tags_list:
                session.run(
                    "UNWIND $tags AS tagName "
                    "MERGE (g:Tag {name:tagName}) "
                    "WITH g "
                    "MATCH (t:Task {id:$id}) "
                    "MERGE (t)-[:HAS_TAG]->(g)",
                    id=task_id,
                    tags=tags_list,
                )
            # return task with collected tags
            rec = session.run(
                "MATCH (t:Task {id:$id}) OPTIONAL MATCH (t)-[:HAS_TAG]->(g:Tag) RETURN t, collect(DISTINCT g.name) AS tags",
                id=task_id,
            ).single()
            node = rec["t"]
            props = dict(node)
            props["tags"] = rec["tags"] or []
            if "created" in props:
                props["created"] = str(props["created"])
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

        tasks: List[Dict] = []
        with self._driver.session() as session:
            if tag:
                # filter by Tag nodes
                result = session.run(
                    "MATCH (t:Task)-[:HAS_TAG]->(g:Tag {name:$tag}) OPTIONAL MATCH (t)-[:HAS_TAG]->(tg:Tag) "
                    "RETURN t, collect(DISTINCT tg.name) AS tags ORDER BY t.created DESC",
                    tag=tag,
                )
            else:
                # apply done filter if present
                if only_done is None:
                    result = session.run(
                        "MATCH (t:Task) OPTIONAL MATCH (t)-[:HAS_TAG]->(g:Tag) RETURN t, collect(DISTINCT g.name) AS tags ORDER BY t.created DESC"
                    )
                else:
                    result = session.run(
                        "MATCH (t:Task) WHERE t.done = $done OPTIONAL MATCH (t)-[:HAS_TAG]->(g:Tag) RETURN t, collect(DISTINCT g.name) AS tags ORDER BY t.created DESC",
                        done=only_done,
                    )

            for r in result:
                node = r["t"]
                props = dict(node)
                # Ensure created is JSON-serializable string
                if "created" in props:
                    props["created"] = str(props["created"])
                props["tags"] = r.get("tags") or []
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

    def get_task(self, task_id: str) -> Optional[Dict]:
        """Return properties for a single task by id, or None if not found."""
        query = "MATCH (t:Task {id:$id}) OPTIONAL MATCH (t)-[:HAS_TAG]->(g:Tag) RETURN t, collect(DISTINCT g.name) AS tags"
        with self._driver.session() as session:
            rec = session.run(query, id=task_id).single()
            if not rec:
                return None
            node = rec["t"]
            props = dict(node)
            props["tags"] = rec.get("tags") or []
            if "created" in props:
                props["created"] = str(props["created"])
            return props

    def delete_task(self, task_id: str) -> bool:
        """Delete a task by id; returns True (always) for now."""
        query = "MATCH (t:Task {id:$id}) DETACH DELETE t"
        with self._driver.session() as session:
            session.run(query, id=task_id)
        return True

    def update_task(self, task_id: str, title: Optional[str] = None, description: Optional[str] = None, tags: Optional[List[str]] = None) -> Optional[Dict]:
        """Update task properties; if `tags` is provided, replace tag relations."""
        sets = []
        params = {"id": task_id}
        if title is not None:
            sets.append("t.title = $title")
            params["title"] = title
        if description is not None:
            sets.append("t.description = $description")
            params["description"] = description

        with self._driver.session() as session:
            if sets:
                set_clause = ", ".join(sets)
                session.run(f"MATCH (t:Task {{id:$id}}) SET {set_clause}", **params)

            if tags is not None:
                # remove existing tag relationships
                session.run("MATCH (t:Task {id:$id})-[r:HAS_TAG]->() DELETE r", id=task_id)
                if tags:
                    session.run(
                        "UNWIND $tags AS tagName MERGE (g:Tag {name:tagName}) WITH g MATCH (t:Task {id:$id}) MERGE (t)-[:HAS_TAG]->(g)",
                        id=task_id,
                        tags=tags,
                    )

            # return updated task
            rec = session.run("MATCH (t:Task {id:$id}) OPTIONAL MATCH (t)-[:HAS_TAG]->(g:Tag) RETURN t, collect(DISTINCT g.name) AS tags", id=task_id).single()
            if not rec:
                return None
            node = rec["t"]
            props = dict(node)
            props["tags"] = rec.get("tags") or []
            if "created" in props:
                props["created"] = str(props["created"])
            return props

    def create_constraints(self) -> None:
        """Create helpful constraints for Task and Tag nodes (if not exists)."""
        with self._driver.session() as session:
            # Unique constraint for Task.id
            session.run(
                "CREATE CONSTRAINT IF NOT EXISTS FOR (t:Task) REQUIRE (t.id) IS UNIQUE"
            )
            # Unique constraint for Tag.name
            session.run(
                "CREATE CONSTRAINT IF NOT EXISTS FOR (g:Tag) REQUIRE (g.name) IS UNIQUE"
            )

    def migrate_tags_to_nodes(self) -> int:
        """Migrate tasks that have a `tags` property (list) into `:Tag` nodes and `HAS_TAG` rels.

        Returns the number of tasks migrated.
        """
        with self._driver.session() as session:
            # find tasks with tags property
            rec = session.run("MATCH (t:Task) WHERE exists(t.tags) RETURN t.id AS id, t.tags AS tags").data()
            count = 0
            for row in rec:
                tid = row["id"]
                tags = row.get("tags") or []
                if not tags:
                    # remove empty property
                    session.run("MATCH (t:Task {id:$id}) REMOVE t.tags", id=tid)
                    continue
                session.run(
                    "UNWIND $tags AS tagName MERGE (g:Tag {name:tagName}) WITH g MATCH (t:Task {id:$id}) MERGE (t)-[:HAS_TAG]->(g)",
                    id=tid,
                    tags=tags,
                )
                session.run("MATCH (t:Task {id:$id}) REMOVE t.tags", id=tid)
                count += 1
            return count

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

    # -- Linking tasks -------------------------------------------------
    def create_link(self, source_id: str, target_id: str, kind: str = "depends") -> bool:
        """Create a LINK relationship from source -> target with a `kind` property.

        Uses a generic relationship type `LINK` and stores the human-readable
        kind in a property so we avoid dynamic relationship types.
        Returns True if the operation completed (node existence not strictly verified here).
        """
        query = (
            "MATCH (a:Task {id:$a}), (b:Task {id:$b}) "
            "MERGE (a)-[r:LINK {kind:$kind}]->(b) RETURN count(r) AS c"
        )
        with self._driver.session() as session:
            rec = session.run(query, a=source_id, b=target_id, kind=kind).single()
            return True

    def delete_link(self, source_id: str, target_id: str, kind: str = "depends") -> int:
        """Delete LINK relationships of given kind from source -> target.

        Returns the number of relationships deleted.
        """
        query = (
            "MATCH (a:Task {id:$a})-[r:LINK {kind:$kind}]->(b:Task {id:$b}) "
            "WITH r, count(r) AS c DELETE r RETURN c"
        )
        with self._driver.session() as session:
            rec = session.run(query, a=source_id, b=target_id, kind=kind).single()
            return int(rec["c"]) if rec and rec["c"] is not None else 0

    def get_links(self, task_id: str) -> List[Dict]:
        """Return linked tasks for a given task id.

        Returns a list of dictionaries with keys: `direction` ("out"|"in"),
        `kind`, and `task` (the linked task properties).
        """
        links: List[Dict] = []
        with self._driver.session() as session:
            # outgoing
            q1 = "MATCH (t:Task {id:$id})-[r:LINK]->(o:Task) RETURN r.kind AS kind, o"
            for rec in session.run(q1, id=task_id):
                node = rec["o"]
                props = dict(node)
                if "created" in props:
                    props["created"] = str(props["created"])
                if "tags" in props and props["tags"] is None:
                    props["tags"] = []
                links.append({"direction": "out", "kind": rec.get("kind"), "task": props})

            # incoming
            q2 = "MATCH (o:Task)-[r:LINK]->(t:Task {id:$id}) RETURN r.kind AS kind, o"
            for rec in session.run(q2, id=task_id):
                node = rec["o"]
                props = dict(node)
                if "created" in props:
                    props["created"] = str(props["created"])
                if "tags" in props and props["tags"] is None:
                    props["tags"] = []
                links.append({"direction": "in", "kind": rec.get("kind"), "task": props})

        return links
