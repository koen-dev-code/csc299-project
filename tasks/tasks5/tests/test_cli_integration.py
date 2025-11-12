import os
import tempfile
import unittest
from taskcli import cli, store

class CLIIntegrationAddTest(unittest.TestCase):
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

    def test_add_and_list_via_cli(self):
        # add
        rc = cli.main(['add', 'Integration Task'])
        self.assertEqual(rc, 0)
        tasks = store.list_tasks(data_path=self.path)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]['title'], 'Integration Task')

if __name__ == '__main__':
    unittest.main()
