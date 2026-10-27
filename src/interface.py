from __future__ import annotations

import subprocess
import sys
from datetime import datetime
from typing import Any

from clypi import ClypiConfig, ClypiFormatter, Command, Positional, Styler, Theme, arg, boxed, configure, prompt, separator, stack
from typing_extensions import override

from src.task_manager import TaskManager


# clear console util
def _clear():
    if sys.platform == "win32":
        subprocess.run("cls", shell=True, check=False)
    else:
        subprocess.run("clear", check=False)


# custom string to datetime parser for clypi prompt inputs
def _parse_date(value: Any) -> datetime:
    if type(value) is not str:
        raise TypeError("Value must be a string.")

    return datetime.strptime(value, "%d-%m-%Y")


# configure clypi
configure(
    ClypiConfig(
        nice_errors=(RuntimeError, TypeError),
        help_formatter=ClypiFormatter(boxed=True, show_option_types=True),
        theme=Theme(
            usage=Styler(fg="cyan", bold=True),
            usage_command=Styler(fg="green", bold=True),
            usage_args=Styler(fg="magenta"),
            section_title=Styler(fg="white", bold=True),
            subcommand=Styler(fg="yellow", bold=True),
            long_option=Styler(fg="cyan", bold=True),
            short_option=Styler(fg="cyan", bold=True),
            positional=Styler(fg="cyan"),
            placeholder=Styler(fg="cyan"),
            prompts=Styler(fg="white", bold=True),
            type_str=Styler(fg="green", bold=True),
        ),
    )
)


class Add(Command):
    """Prompts a user for task details and creates adds its to the task manager."""

    db_name: str = arg(help="The name of the tasks database to use.", default="tasks.db")

    title: Positional[str] = arg(help="The title of the task.", prompt="What is the title of the task you would like to add?")
    description: Positional[str] = arg(help="The description of the task.", prompt="What is the description?")
    due_date: Positional[datetime] = arg(
        help="The tasks due date.", prompt="What is the due date? (format: dd-mm-yyyy)", parser=_parse_date
    )

    @override
    async def run(self) -> None:
        task_manager = TaskManager(self.db_name)

        result = task_manager.add_task(self.title, self.description, self.due_date)

        # runtimeerror beats using exception, dont judge me
        if not result:
            raise RuntimeError("Failed to add the task.")

        print(boxed(f"Added {self.title}.", title="Success", width=100, color="green"))


class Delete(Command):
    """Prompts a user for a task to be removed from the task manager."""

    db_name: str = arg(help="The name of the tasks database to use.", default="tasks.db")

    title: Positional[str] = arg(help="The title of the task to delete.", prompt="What is the name of the task you would like to delete?")

    @override
    async def run(self) -> None:
        task_manager = TaskManager(self.db_name)

        result = task_manager.delete_task(self.title)

        if not result:
            raise RuntimeError("Failed to delete the task.")

        print(boxed(f"Deleted {self.title}.", title="Success", width=100, color="green"))


class List(Command):
    """Lists the current tasks within the task manager"""

    db_name: str = arg(help="The name of the tasks database to use.", default="tasks.db")

    status: Positional[str | None] = arg(help="The task status to filter by.", default=None)

    @override
    async def run(self) -> None:
        task_manager = TaskManager(self.db_name)

        tasks = task_manager.tasks(self.status)

        if not tasks:
            raise RuntimeError("No tasks found.")

        title_col = boxed([task.title for task in tasks], title="Title", width=25)
        desc_col = boxed([task.description[:10] for task in tasks], title="Description", width=25)
        date_col = boxed([datetime.strptime(task.due_date, "%Y-%m-%d").strftime("%d-%m-%Y") for task in tasks], title="Due Date", width=25)
        status_col = boxed([task.status for task in tasks], title="Status", width=25)

        print(separator(title="Tasks", width=100, color="cyan"))
        print(stack(title_col, desc_col, date_col, status_col, padding=0))


class Cli(Command):
    subcommand: Add | Delete | List | None

    db_name: str = arg(help="The name of the tasks database to use.", default="tasks.db")

    @override
    async def run(self) -> None:
        options: dict[str, type[Command]] = {"1": Add, "2": Delete, "3": List}
        options_prompt: str = """
            What would you like to do?
        
            (1) Add a task.
            (2) Delete a task.
            (3) List current tasks.
        
            Run --help to see the list of commands.

            CTRL+C to quit.
            """

        # not a massive fan of how ive done this tbh
        if self.subcommand is None:
            while True:
                try:
                    _clear()
                    option = prompt(boxed(options_prompt, width=100, align="center", color="cyan") + "\nOption")
                    _clear()

                    command = options.get(option)

                    if command is None:
                        print("Invalid option.")
                    else:
                        await command.parse(["--db_name", self.db_name]).astart()

                    input("Press enter to continue...")

                except (EOFError, KeyboardInterrupt):
                    sys.exit(0)
