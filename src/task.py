from __future__ import annotations


class Task:
    """
    A class to represent a task in the task management application.

    Attributes:
        title (str): The title of the task.
        description (str): A brief description of the task.
        due_date (str): The due date of the task in 'DD-MM-YYYY' format.
        status (str): The current status of the task, defaults to 'pending'.
    """

    def __init__(
        self, title: str, description: str, due_date: str, status: str = "pending"
    ) -> None:
        """
        Initialise a Task object with title, description, due date, and status.

        Args:
            title (str): The title of the task.
            description (str): A brief description of the task.
            due_date (str): The due date of the task in 'YYYY-MM-DD' format.
            status (str, optional): The status of the task. Defaults to 'pending'.
        """

        self.title = title
        self.description = description
        self.due_date = due_date
        self.status = status
