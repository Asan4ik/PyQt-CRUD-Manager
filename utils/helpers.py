import json
import uuid
from datetime import datetime
from pathlib import Path

DEFAULT_PATH = Path("data/tasks.json")
STATUSES = ["todo", "inprogress", "done"]
DATE_FORMAT = "%Y-%m-%d"
DISPLAY_FORMAT = "%d %b %Y"


def load_tasks(filepath: Path = DEFAULT_PATH) -> list[dict]:
    """Load tasks from a JSON file. Returns empty list if file doesn't exist or is invalid."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_tasks(tasks: list[dict], filepath: Path = DEFAULT_PATH) -> None:
    """Save tasks list to a JSON file, creating directories if needed."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)


def create_task(
    title: str,
    description: str = "",
    status: str = "todo",
    deadline: str = "",
) -> dict:
    """Create and return a new task dict with a unique ID and creation timestamp."""
    if status not in STATUSES:
        raise ValueError(f"Invalid status '{status}'. Must be one of {STATUSES}.")
    return {
        "id": str(uuid.uuid4()),
        "title": title.strip(),
        "description": description.strip(),
        "status": status,
        "created_at": datetime.now().strftime(DATE_FORMAT),
        "deadline": deadline.strip(),
    }


def add_task(
    tasks: list[dict],
    title: str,
    description: str = "",
    status: str = "todo",
    deadline: str = "",
) -> dict:
    """Create a new task, append it to the list, and return it."""
    task = create_task(title, description, status, deadline)
    tasks.append(task)
    return task


def delete_task(tasks: list[dict], task_id: str) -> bool:
    """Remove a task by its ID. Returns True if found and removed, False otherwise."""
    for i, task in enumerate(tasks):
        if task.get("id") == task_id:
            tasks.pop(i)
            return True
    return False


def get_tasks_by_status(tasks: list[dict], status: str) -> list[dict]:
    """Return tasks matching the given status, sorted by deadline then created_at."""
    filtered = [t for t in tasks if t.get("status") == status]
    return sort_tasks(filtered)


def sort_tasks(tasks: list[dict]) -> list[dict]:
    """Sort tasks: ones with a deadline first (earliest first), then by creation date."""
    def sort_key(task: dict):
        deadline = task.get("deadline", "")
        created = task.get("created_at", "")
        # Tasks with a deadline sort before those without
        has_deadline = 0 if deadline else 1
        return (has_deadline, deadline, created)

    return sorted(tasks, key=sort_key)


def format_date(date_str: str) -> str:
    """Convert stored date string (YYYY-MM-DD) to a human-readable format."""
    try:
        return datetime.strptime(date_str, DATE_FORMAT).strftime(DISPLAY_FORMAT)
    except (ValueError, TypeError):
        return ""
