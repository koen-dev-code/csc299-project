import os
import tempfile
import unittest
from taskcli import cli, store

class CLIIntegrationDeleteTest(unittest.TestCase):
    def setUp(self):
        fd, self.path = tempfile.mkstemp(prefix='taskcli_cli_test_', suffix='.json')
        os.close(fd)
        self.env = os.environ.copy()
        self.env['TASKCLI_DATA'] = self.path

    def tearDown(self):
        try:
            os.remove(self.path)
        except OSError:
            pass

    def test_delete_via_cli(self):
        tid = store.add_task('To be deleted', data_path=self.path)
        rc = cli.main(['delete', tid])
        self.assertEqual(rc, 0)
        tasks = store.list_tasks(data_path=self.path)
        self.assertFalse(any(t['id'] == tid for t in tasks))

if __name__ == '__main__':
    unittest.main()
