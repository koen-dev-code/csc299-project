import os
from datetime import datetime
from typing import List, Optional, Dict, Any

# load environment from a .env located in the project root (three directories up)
from dotenv import load_dotenv

env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
load_dotenv(env_path)

from neo4j import GraphDatabase, basic_auth


class TaskManager:
    """Neo4j-backed task manager. Tasks are stored as :Task nodes with properties:
       - id: integer (unique)
       - title: string
       - description: string
       - tags: list<string>
       - created_at: ISO timestamp
    """

    def __init__(self, path: Optional[str] = None):
        # path parameter is repurposed as optional Neo4j URI. If not provided,
        # environment variables are used, otherwise defaults are applied.
        uri = path or os.environ.get("NEO4J_URI")
        user = os.environ.get("NEO4J_USER")
        password = os.environ.get("NEO4J_PASSWORD")
        self.driver = GraphDatabase.driver(uri, auth=basic_auth(user, password))
        # ensure constraint exists
        with self.driver.session() as s:
            # create uniqueness constraint for Task.id (supports Neo4j 4.x+)
            try:
                s.run("CREATE CONSTRAINT IF NOT EXISTS FOR (t:Task) REQUIRE t.id IS UNIQUE")
            except Exception:
                # older server versions might use legacy syntax; ignore failures
                pass

    def close(self) -> None:
        try:
            self.driver.close()
        except Exception:
            pass

    def _next_id(self) -> int:
        with self.driver.session() as s:
            rec = s.run("MATCH (t:Task) RETURN coalesce(max(t.id), 0) AS maxid").single()
            maxid = rec["maxid"] if rec and "maxid" in rec else 0
            return int(maxid) + 1

    def add_task(self, title: str, description: str = "", tags: Optional[List[str]] = None) -> Dict[str, Any]:
        tags = tags or []
        tid = self._next_id()
        created = datetime.utcnow().isoformat() + "Z"
        with self.driver.session() as s:
            rec = s.run(
                "CREATE (t:Task {id:$id, title:$title, description:$description, tags:$tags, created_at:$created_at}) "
                "RETURN t.id AS id, t.title AS title, t.description AS description, t.tags AS tags, t.created_at AS created_at",
                id=tid,
                title=title,
                description=description,
                tags=tags,
                created_at=created,
            ).single()
            return {
                "id": rec["id"],
                "title": rec["title"],
                "description": rec.get("description", "") if rec else description,
                "tags": rec.get("tags", []) if rec else tags,
                "created_at": rec.get("created_at") if rec else created,
            }

    def remove_task(self, task_id: int) -> bool:
        with self.driver.session() as s:
            exists = s.run("MATCH (t:Task {id:$id}) RETURN count(t) AS c", id=task_id).single()
            if not exists or exists["c"] == 0:
                return False
            s.run("MATCH (t:Task {id:$id}) DETACH DELETE t", id=task_id)
            return True

    def _node_to_task(self, record) -> Dict[str, Any]:
        # record should expose id, title, description, tags, created_at
        return {
            "id": record.get("id"),
            "title": record.get("title"),
            "description": record.get("description", "") if record.get("description") is not None else "",
            "tags": list(record.get("tags", [])) if record.get("tags") is not None else [],
            "created_at": record.get("created_at"),
        }

    def get_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        with self.driver.session() as s:
            rec = s.run(
                "MATCH (t:Task {id:$id}) RETURN t.id AS id, t.title AS title, t.description AS description, t.tags AS tags, t.created_at AS created_at",
                id=task_id,
            ).single()
            if not rec:
                return None
            return self._node_to_task(rec)

    def list_tasks(self, tag: Optional[str] = None) -> List[Dict[str, Any]]:
        with self.driver.session() as s:
            if tag is None:
                res = s.run(
                    "MATCH (t:Task) RETURN t.id AS id, t.title AS title, t.description AS description, t.tags AS tags, t.created_at AS created_at ORDER BY t.id"
                )
            else:
                # filter tasks where tag is present in tags list (case-sensitive matching of stored tags)
                res = s.run(
                    "MATCH (t:Task) WHERE $tag IN t.tags "
                    "RETURN t.id AS id, t.title AS title, t.description AS description, t.tags AS tags, t.created_at AS created_at ORDER BY t.id",
                    tag=tag,
                )
            return [self._node_to_task(r) for r in res]

    def update_task(self, task_id: int, title: Optional[str] = None, description: Optional[str] = None, tags: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        # Build a dynamic SET clause safely by providing only the params that are not None.
        set_clauses = []
        params = {"id": task_id}
        if title is not None:
            set_clauses.append("t.title = $title")
            params["title"] = title
        if description is not None:
            set_clauses.append("t.description = $description")
            params["description"] = description
        if tags is not None:
            set_clauses.append("t.tags = $tags")
            params["tags"] = tags

        if not set_clauses:
            return self.get_task(task_id)  # nothing to change

        cypher = "MATCH (t:Task {id:$id}) SET " + ", ".join(set_clauses) + " RETURN t.id AS id, t.title AS title, t.description AS description, t.tags AS tags, t.created_at AS created_at"
        with self.driver.session() as s:
            rec = s.run(cypher, **params).single()
            if not rec:
                return None
            return self._node_to_task(rec)

    # keep a destructor/close hook
    def __del__(self):
        try:
            self.close()
        except Exception:
            pass


# quick demo when run directly
if __name__ == "__main__":
    tm = TaskManager()
    print("Connected to Neo4j")
    sample = tm.add_task("Example task", "This is a sample added when invoking V2database directly.", ["example", "init"])
    print("Added:", sample)