from dotenv import load_dotenv
import os, sys, traceback
from neo4j import GraphDatabase

load_dotenv()
uri = os.getenv("NEO4J_URI")
user = os.getenv("NEO4J_USER")
password = os.getenv("NEO4J_PASSWORD")
print(f"NEO4J_URI={'SET' if uri else 'MISSING'}, NEO4J_USER={'SET' if user else 'MISSING'}")
if not (uri and user and password):
    print("Missing one or more NEO4J env vars; cannot test connection.")
    sys.exit(3)

try:
    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session() as session:
        print("Opening session and running simple query...")
        result = session.run("RETURN 1 AS v")
        row = result.single()
        print("Query result:", row["v"]) if row else print("No rows returned")
    driver.close()
    print("Connection test: SUCCESS")
    sys.exit(0)
except Exception as e:
    print("Connection test: FAILED")
    traceback.print_exc()
    try:
        driver.close()
    except Exception:
        pass
    sys.exit(4)
