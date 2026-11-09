import os
import unittest

from src.interface import Add, Cli, Delete, List
from src.task_manager import TaskManager


class TestInterface(unittest.TestCase):
    """
    Unit tests for CLI functionalities including add, delete and list.
    """

    _TEST_DB_NAME = "test_tasks.db"

    def tearDown(self) -> None:
        """
        Clean up the test environment by removing any test-created tables.
        """

        # not the cleanest approach but works for testing
        task_manager = TaskManager(self._TEST_DB_NAME)
        task_manager._cursor.execute("DROP TABLE IF EXISTS tasks")  # type: ignore
        task_manager._db.close()  # type: ignore

    @classmethod
    def tearDownClass(cls) -> None:
        """
        Clean up any test-created database files.
        """

        os.remove(cls._TEST_DB_NAME)

    async def test_add_command(self) -> None:
        command = Add.parse(
            ["test", "test desc", "12-12-2026", "--db_name", self._TEST_DB_NAME]
        )

        command.start()

    async def test_add_command_bad_date(self) -> None:
        """
        Unit test to check if add command raises exception with bad dates
        """

        command_past_date = Add.parse(
            ["test", "test desc", "12-12-2024", "--db_name", self._TEST_DB_NAME]
        )

        command_bad_format = Add.parse(
            ["test", "test desc", "2024-12-12", "--db_name", self._TEST_DB_NAME]
        )

        self.assertRaisesRegex(RuntimeError, "Failed", command_past_date.start)
        self.assertRaisesRegex(RuntimeError, "Failed", command_bad_format.start)

    async def test_delete_command(self) -> None:
        """
        Unit test to check if delete command runs and raises correct exception
        """

        Add.parse(
            ["test", "test desc", "12-12-2026", "--db_name", self._TEST_DB_NAME]
        ).start()

        command = Delete.parse(["test", "--db_name", self._TEST_DB_NAME])
        command_arg = Delete.parse(["test1", "--db_name", self._TEST_DB_NAME])

        command.start()

        self.assertRaisesRegex(RuntimeError, "Failed", command_arg.start)

    async def test_list_command(self) -> None:
        """
        Unit test to check list command runs and filters as intended.
        """

        Add.parse(
            ["test1", "test desc", "12-12-2026", "--db_name", self._TEST_DB_NAME]
        ).start()

        Add.parse(
            ["test2", "test desc", "12-12-2026", "--db_name", self._TEST_DB_NAME]
        ).start()

        command = List.parse(["pending", "--db_name", self._TEST_DB_NAME])
        command_arg = List.parse(["test", "--db_name", self._TEST_DB_NAME])

        command.start()

        self.assertRaisesRegex(RuntimeError, "No tasks found", command_arg.start)

    async def test_cli_subcommand(self) -> None:
        """
        Unit test to check subcommand and option inheritence.
        """

        Cli.parse(
            ["--db_name", self._TEST_DB_NAME, "add", "test", "test desc", "12-12-2026"]
        ).start()

        Cli.parse(["--db_name", self._TEST_DB_NAME, "list", "test"]).start()

        Cli.parse(["--db_name", self._TEST_DB_NAME, "delete", "test"]).start()
