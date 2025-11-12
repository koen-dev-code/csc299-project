import os
import tempfile
import unittest
from taskcli import cli, store

class CLITestEnvRespect(unittest.TestCase):
    def test_cli_respects_taskcli_data_env(self):
        fd, path = tempfile.mkstemp(prefix='taskcli_cli_test_env_', suffix='.json')
        os.close(fd)
        try:
            # set env so cli writes to this file
            saved = os.environ.copy()
            os.environ['TASKCLI_DATA'] = path
            rc = cli.main(['add', 'Env Task'])
            self.assertEqual(rc, 0)
            tasks = store.list_tasks(data_path=path)
            self.assertEqual(len(tasks), 1)
            self.assertEqual(tasks[0]['title'], 'Env Task')
        finally:
            os.environ.clear()
            os.environ.update(saved)
            try:
                os.remove(path)
            except OSError:
                pass

if __name__ == '__main__':
    unittest.main()
