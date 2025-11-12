import os
import tempfile
import unittest
from taskcli import store


class StoreTests(unittest.TestCase):
    def setUp(self):
        fd, self.path = tempfile.mkstemp(prefix='taskcli_test_', suffix='.json')
        os.close(fd)

    def tearDown(self):
        try:
            os.remove(self.path)
        except OSError:
            pass

    def test_add_and_list(self):
        tid = store.add_task('Test task', 'desc', data_path=self.path)
        tasks = store.list_tasks(data_path=self.path)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]['id'], tid)
        self.assertEqual(tasks[0]['title'], 'Test task')

    def test_delete(self):
        tid = store.add_task('To remove', data_path=self.path)
        ok = store.delete_task(tid, data_path=self.path)
        self.assertTrue(ok)
        tasks = store.list_tasks(data_path=self.path)
        self.assertEqual(len(tasks), 0)

    def test_delete_missing(self):
        ok = store.delete_task('nonexistent', data_path=self.path)
        self.assertFalse(ok)

    def test_empty_title_rejected(self):
        with self.assertRaises(ValueError):
            store.add_task('   ', data_path=self.path)


if __name__ == '__main__':
    unittest.main()
