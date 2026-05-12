import unittest

from utils.helpers import add_task, create_task, get_tasks_by_status, normalize_priority


class TestTaskPriorities(unittest.TestCase):
    def test_create_task_saves_priority(self):
        task = create_task("Important", priority=3)

        self.assertEqual(task["priority"], 3)

    def test_normalize_priority_keeps_values_between_zero_and_three(self):
        self.assertEqual(normalize_priority(None), 0)
        self.assertEqual(normalize_priority("2"), 2)
        self.assertEqual(normalize_priority(10), 3)
        self.assertEqual(normalize_priority(-1), 0)

    def test_tasks_sort_by_priority_before_deadline(self):
        tasks = [
            {
                "id": "normal",
                "title": "Normal task",
                "status": "todo",
                "priority": 0,
                "created_at": "2026-05-01",
                "deadline": "2026-05-01",
            },
            {
                "id": "high",
                "title": "High priority task",
                "status": "todo",
                "priority": 3,
                "created_at": "2026-05-02",
                "deadline": "2026-05-10",
            },
            {
                "id": "medium",
                "title": "Medium priority task",
                "status": "todo",
                "priority": 2,
                "created_at": "2026-05-03",
                "deadline": "",
            },
        ]

        sorted_ids = [task["id"] for task in get_tasks_by_status(tasks, "todo")]

        self.assertEqual(sorted_ids, ["high", "medium", "normal"])

    def test_add_task_defaults_to_no_priority(self):
        tasks = []
        task = add_task(tasks, "Default priority")

        self.assertEqual(task["priority"], 0)
        self.assertEqual(tasks, [task])


if __name__ == "__main__":
    unittest.main()
