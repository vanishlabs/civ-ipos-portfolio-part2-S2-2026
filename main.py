from datetime import datetime

from src.task_manager import TaskManager

_task_manager = TaskManager("tasks.db")


def main():  # noqa: C901
    while True:
        print("\nTask Manager CLI")
        print("1. Add Task")
        print("2. Delete Task")
        print("3. List Tasks")
        print("4. Exit")

        choice = input("Enter your choice: ")
        if choice == "1":
            title = input("Title: ")
            description = input("Description: ")
            due_date = input("Due Date (DD-MM-YYYY): ")
            _task_manager.add_task(
                title, description, datetime.strptime(due_date, "%d-%m-%Y")
            )
        elif choice == "2":
            title = input("Title of the task to delete: ")
            if _task_manager.delete_task(title):
                print("Task deleted successfully.")
            else:
                print("Task not found.")
        elif choice == "3":
            tasks = _task_manager.tasks()

            for task in tasks:
                print(f"### Title: {task.title} | Due: {task.due_date} | Status: {task.status} ###")  # noqa: E501 B950
                print(task.description + '\n')
        elif choice == "4":
            print("Exiting Task Manager.")
            break
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
