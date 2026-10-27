import os
import unittest
from datetime import datetime

from src.task_manager import TaskManager


class TestTaskManager(unittest.TestCase):
    """
    Unit tests for Task Manager functionalities including creating, adding and deleting from the tasks database.
    """

    _TEST_DB_NAME = "test_tasks.db"

    def setUp(self) -> None:
        """
        Set up the test environment by instantiating our TaskManager object which creates
        a new database file with the specified name.
        """

        self._task_manager = TaskManager(self._TEST_DB_NAME)

    def tearDown(self) -> None:
        """
        Clean up the test environment by removing any test-created tables.
        """

        # not the cleanest approach but works for testing
        self._task_manager._cursor.execute("DROP TABLE IF EXISTS tasks") # type: ignore
        self._task_manager._db.close() # type: ignore

    @classmethod
    def tearDownClass(cls) -> None:
        """
        Clean up any test-created database files.
        """

        os.remove(cls._TEST_DB_NAME)

    def test_add_task(self) -> None:
        """
        Test adding a new task to the tasks database.
        Verify that the task is successfully added and the table row count increases.
        """

        result = self._task_manager.add_task("Test Task", "Description", datetime(2027, 1, 1))

        self.assertTrue(result)
        self.assertEqual(len(self._task_manager.tasks()), 1)

    def test_add_duplicate_task(self) -> None:
        """
        Test adding a duplicate task with the same title.
        Verify that duplicates are not allowed, it is case insensitive and the function returns false.
        """

        self._task_manager.add_task("Test Task", "Description", datetime(2027, 1, 1))
        result = self._task_manager.add_task("test task", "New Description", datetime(2028, 2, 2))

        self.assertFalse(result)

    def test_add_invalid_due_date(self) -> None:
        """
        Test adding a task with an invalid due date format.
        Verify that the function handles invalid input and the function returns false.
        """

        result = self._task_manager.add_task("Test Task", "Description", datetime(2024, 1, 1))

        self.assertFalse(result)

    def test_delete_task(self) -> None:
        """
        Test deleting a task by its title.
        Verify that the task is removed from the database and the table row count decreases.
        """

        self._task_manager.add_task("Task to Delete", "Description", datetime(2027, 1, 1))

        result = self._task_manager.delete_task("Task to Delete")

        self.assertTrue(result)
        self.assertEqual(len(self._task_manager.tasks()), 0)


if __name__ == "__main__":
    unittest.main()
