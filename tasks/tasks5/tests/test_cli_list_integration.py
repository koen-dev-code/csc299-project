import os
import tempfile
import unittest
from taskcli import cli, store

class CLIIntegrationListTest(unittest.TestCase):
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

    def test_list_formats(self):
        # add two tasks
        t1 = store.add_task('Task 1', data_path=self.path)
        t2 = store.add_task('Task 2', data_path=self.path)
        # call list human format
        rc = cli.main(['list'])
        self.assertEqual(rc, 0)
        tasks = store.list_tasks(data_path=self.path)
        self.assertEqual(len(tasks), 2)

if __name__ == '__main__':
    unittest.main()
