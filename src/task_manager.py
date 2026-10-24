from __future__ import annotations

import sqlite3
from datetime import datetime

from src.task import Task


class TaskManager:
    """
    Essentially an sqlite3 db wrapper/service used to create, delete and manage daily tasks.
    """

    def __init__(self, db_name: str) -> None:
        self._db = sqlite3.connect(db_name)
        self._db.row_factory = sqlite3.Row
        self._cursor = self._db.cursor()
        self._db.autocommit = True
        with self._db:
            self._cursor.execute(
                "CREATE TABLE IF NOT EXISTS tasks ("
                "title TEXT PRIMARY KEY COLLATE NOCASE,"
                "description TEXT NOT NULL,"
                "due_date TEXT NOT NULL DEFAULT CURRENT_DATE,"
                "status TEXT NOT NULL DEFAULT 'pending',"
                "CHECK (due_date >= CURRENT_DATE)"
                ")"
            )

    # hoping you might be able to answer a question:
    # __del__ should be called when the future object ref count is <1
    # so why when i call my classTearDown method does it raise an exception
    # due to the connection still being open and in use, even when explicitly calling the gc
    # in the end i just ended up closing it manually after each test but still curious about
    # this and the way gc is handled
    def __del__(self) -> None:
        self._db.close()

    def add_task(self, title: str, description: str, due_date: datetime) -> bool:
        """
        Add a new task to the tasks table.

        Args:
            title (str): The title of the new task, must be unique.
            description (str): A brief description of the task.
            due_date (datetime): The due date of the task.

        Returns:
            bool: True if the task is added successfully, False otherwise.
        """

        try:
            with self._db:
                result = self._cursor.execute(
                    "INSERT INTO tasks (title, description, due_date) VALUES (?, ?, ?)", (title, description, due_date.strftime("%Y-%m-%d"))
                )

                return result.rowcount > 0

        except sqlite3.IntegrityError:
            return False

    def delete_task(self, title: str) -> bool:
        """
        Delete a task from the tasks table based on its title.

        Args:
            title (str): The title of the task to be deleted.

        Returns:
            bool: True if the task was found and deleted, False otherwise.
        """

        try:
            with self._db:
                result = self._cursor.execute(f"DELETE FROM tasks WHERE title = '{title}'")

                return result.rowcount > 0

        except sqlite3.IntegrityError:
            return False

    def tasks(self, status: str | None = None) -> list[Task]:
        """
        Display tasks in the tasks table, optionally filtered by status.

        Args:
            status (str, optional): The status to filter tasks (eg. 'pending').

        Returns:
            list[Task]: Returns the rows as a list.
        """

        try:
            # i hate this so much but i hate python's ternary statements with string interpolation even more
            query = "SELECT * FROM tasks"

            if status is not None:
                query += f" WHERE status = '{status}'"

            with self._db:
                result = self._cursor.execute(query)

            rows = result.fetchall()

            return [Task(row["title"], row["description"], row["due_date"], row["status"]) for row in rows]

        except sqlite3.IntegrityError:
            return []
