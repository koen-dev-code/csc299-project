import os
import tempfile
import json
import sys
import unittest

from cli_db import main as cli_main, load_db


def run(argv):
    return cli_main(argv)


class TestCliDb(unittest.TestCase):
    def test_add_get_delete_cycle(self):
        with tempfile.TemporaryDirectory() as td:
            db_path = os.path.join(td, "testdb.json")

            # Add key
            rc = run(["--db", db_path, "add", "name", "alice"])
            self.assertEqual(rc, 0)

            # Get key
            rc = run(["--db", db_path, "get", "name"])
            self.assertEqual(rc, 0)

            # Confirm file contents
            with open(db_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.assertIn("name", data)
            self.assertEqual(data["name"]["value"], "alice")

            # Delete key
            rc = run(["--db", db_path, "delete", "name"])
            self.assertEqual(rc, 0)

            # Confirm deletion
            data = load_db(db_path)
            self.assertNotIn("name", data)

    def test_list_multiple(self):
        with tempfile.TemporaryDirectory() as td:
            db_path = os.path.join(td, "testdb2.json")
            run(["--db", db_path, "add", "k1", "v1"])
            run(["--db", db_path, "add", "k2", "v2"])

            rc = run(["--db", db_path, "list"])
            self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
