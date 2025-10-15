# graph_pkm/database.py

import os
import uuid
from datetime import datetime, timezone
from neo4j import GraphDatabase as Neo4jGraphDatabase
from dotenv import load_dotenv

class GraphDatabase:
    """
    A class to handle connections and queries to a Neo4j database.
    It uses the official neo4j driver and python-dotenv to manage configuration.
    """

    def __init__(self):
        """
        Initializes the database connection by loading credentials from a .env file.
        """
        load_dotenv()
        uri = os.getenv("NEO4J_URI")
        user = os.getenv("NEO4J_USER")
        password = os.getenv("NEO4J_PASSWORD")

        if not all([uri, user, password]):
            raise ValueError("NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD must be set in .env file")

        self._driver = Neo4jGraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        """
        Closes the database driver connection.
        """
        if self._driver:
            self._driver.close()

    def execute_query(self, query: str, parameters: dict = None):
        """
        Executes a Cypher query against the database.

        This method handles session and transaction management automatically
        using `execute_write` for data modification queries.

        Args:
            query (str): The Cypher query to execute.
            parameters (dict, optional): A dictionary of parameters for the query.

        Returns:
            The result of the query execution.
        """
        with self._driver.session() as session:
            # We use execute_write for queries that modify the graph (CREATE, MERGE, SET, DELETE)
            result = session.execute_write(self._execute_transaction, query, parameters)
            return result

    @staticmethod
    def _execute_transaction(tx, query, parameters=None):
        """Helper function to be passed to session.execute_write."""
        result = tx.run(query, parameters)
        # To return a value from the transaction, we may need to consume the result
        # For a simple CREATE returning a value, this is often sufficient.
        return result.single()

    def add_note(self, content: str) -> str:
        """
        Creates a new :Note node in the database.

        Args:
            content (str): The text content of the note.

        Returns:
            str: The UUID of the newly created note.
        """
        note_uuid = str(uuid.uuid4())
        # Ensure timestamp is timezone-aware (UTC)
        now_utc = datetime.now(timezone.utc)

        # Cypher query to create a new Note node.
        # MERGE is used here on uuid to guarantee uniqueness, though uuid4 is highly unlikely to collide.
        # ON CREATE sets properties only when the node is first created.
        # We use parameters ($param) to prevent Cypher injection.
        query = (
            "MERGE (n:Note {uuid: $uuid}) "
            "ON CREATE SET "
            "  n.content = $content, "
            "  n.created_at = $created_at, "
            "  n.updated_at = $updated_at "
            "RETURN n.uuid AS uuid"
        )
        parameters = {
            "uuid": note_uuid,
            "content": content,
            "created_at": now_utc,
            "updated_at": now_utc,
        }

        result = self.execute_query(query, parameters)
        
        # The result from execute_query is a Record object, access the value by key
        return result["uuid"] if result else None