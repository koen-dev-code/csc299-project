import os
import tempfile
import unittest
from taskcli import cli, store

class CLIIntegrationDeleteTest(unittest.TestCase):
    def setUp(self):
        fd, self.path = tempfile.mkstemp(prefix='taskcli_cli_test_', suffix='.json')
        os.close(fd)
        # ensure CLI sees the temp data file via environment
        self._saved_env = os.environ.copy()
        os.environ['TASKCLI_DATA'] = self.path

    def tearDown(self):
        try:
            os.remove(self.path)
        except OSError:
            pass
        # restore environment
        os.environ.clear()
        os.environ.update(self._saved_env)

    def test_delete_via_cli(self):
        tid = store.add_task('To be deleted', data_path=self.path)
        rc = cli.main(['delete', tid])
        self.assertEqual(rc, 0)
        tasks = store.list_tasks(data_path=self.path)
        self.assertFalse(any(t['id'] == tid for t in tasks))

if __name__ == '__main__':
    unittest.main()
