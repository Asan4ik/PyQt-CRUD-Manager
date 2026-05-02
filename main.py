import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QStackedWidget, QDialog,
    QLineEdit, QTextEdit, QComboBox,
    QFileDialog, QScrollArea, QFrame,
    QMessageBox, QDateEdit
)
from PySide6.QtCore import Qt, QDate

from utils.helpers import (
    load_tasks, save_tasks, add_task,
    delete_task, get_tasks_by_status, format_date
)

DEFAULT_PATH = Path("data/tasks.json")

# ── Styles ────────────────────────────────────────────────────────────────────

SIDEBAR_STYLE = "QWidget#sidebar { background-color: #1e1e2e; }"

NAV_BUTTON_STYLE = """
    QPushButton {
        background-color: transparent;
        color: #cdd6f4;
        font-size: 14px;
        font-weight: bold;
        padding: 12px 20px;
        text-align: left;
        border: none;
        border-radius: 8px;
    }
    QPushButton:hover { background-color: #313244; }
    QPushButton:checked { background-color: #45475a; color: #cba6f7; }
"""

ADD_BUTTON_STYLE = """
    QPushButton {
        background-color: #cba6f7;
        color: #1e1e2e;
        font-size: 13px;
        font-weight: bold;
        padding: 10px;
        border: none;
        border-radius: 8px;
    }
    QPushButton:hover { background-color: #b4befe; }
"""

LOAD_BUTTON_STYLE = """
    QPushButton {
        background-color: transparent;
        color: #89b4fa;
        font-size: 12px;
        padding: 8px 10px;
        border: 1px solid #45475a;
        border-radius: 8px;
    }
    QPushButton:hover { background-color: #313244; }
"""

TASK_CARD_STYLE = """
    QFrame {
        background-color: #313244;
        border-radius: 10px;
    }
"""

DELETE_BTN_STYLE = """
    QPushButton {
        background-color: transparent;
        color: #f38ba8;
        font-size: 16px;
        border: none;
        border-radius: 4px;
        padding: 2px 6px;
    }
    QPushButton:hover { background-color: #45475a; }
"""

INPUT_STYLE = """
    QLineEdit, QTextEdit, QComboBox, QDateEdit {
        background-color: #313244;
        color: #cdd6f4;
        border: 1px solid #45475a;
        border-radius: 6px;
        padding: 6px;
        font-size: 13px;
    }
    QLineEdit:focus, QTextEdit:focus, QDateEdit:focus { border-color: #cba6f7; }
"""

DIALOG_BTN_STYLE = """
    QPushButton {
        background-color: #cba6f7;
        color: #1e1e2e;
        font-weight: bold;
        padding: 8px 20px;
        border: none;
        border-radius: 6px;
    }
    QPushButton:hover { background-color: #b4befe; }
"""

CHECKBOX_STYLE = """
    QCheckBox {
        color: #a6adc8;
        font-size: 12px;
        spacing: 6px;
    }
"""

# ── Add Task Dialog ───────────────────────────────────────────────────────────

class AddTaskDialog(QDialog):
    """Modal dialog for entering new task details."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Task")
        self.setMinimumWidth(420)
        self.setStyleSheet("background-color: #1e1e2e; color: #cdd6f4;")

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        layout.addWidget(self._label("Title *"))
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter task title...")
        self.title_input.setStyleSheet(INPUT_STYLE)
        layout.addWidget(self.title_input)

        layout.addWidget(self._label("Description (optional)"))
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Enter details...")
        self.desc_input.setFixedHeight(80)
        self.desc_input.setStyleSheet(INPUT_STYLE)
        layout.addWidget(self.desc_input)

        layout.addWidget(self._label("Status"))
        self.status_input = QComboBox()
        self.status_input.addItems(["To Do", "In Progress", "Done"])
        self.status_input.setStyleSheet(INPUT_STYLE)
        layout.addWidget(self.status_input)

        layout.addWidget(self._label("Deadline (optional)"))
        # Row: date picker + "No deadline" checkbox
        deadline_row = QHBoxLayout()
        self.deadline_input = QDateEdit()
        self.deadline_input.setCalendarPopup(True)
        self.deadline_input.setDate(QDate.currentDate())
        self.deadline_input.setStyleSheet(INPUT_STYLE)
        self.deadline_input.setDisplayFormat("dd MMM yyyy")

        from PySide6.QtWidgets import QCheckBox
        self.no_deadline_cb = QCheckBox("No deadline")
        self.no_deadline_cb.setStyleSheet(CHECKBOX_STYLE)
        self.no_deadline_cb.setChecked(True)
        self.deadline_input.setEnabled(False)
        self.no_deadline_cb.toggled.connect(
            lambda checked: self.deadline_input.setEnabled(not checked)
        )

        deadline_row.addWidget(self.deadline_input)
        deadline_row.addWidget(self.no_deadline_cb)
        layout.addLayout(deadline_row)

        layout.addSpacing(8)
        confirm_btn = QPushButton("Add Task")
        confirm_btn.setStyleSheet(DIALOG_BTN_STYLE)
        confirm_btn.clicked.connect(self.accept)
        layout.addWidget(confirm_btn)

    def _label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet("color: #a6adc8; font-size: 12px; font-weight: bold;")
        return lbl

    def get_values(self) -> tuple[str, str, str, str]:
        status_map = {"To Do": "todo", "In Progress": "inprogress", "Done": "done"}
        deadline = ""
        if not self.no_deadline_cb.isChecked():
            deadline = self.deadline_input.date().toString("yyyy-MM-dd")
        return (
            self.title_input.text().strip(),
            self.desc_input.toPlainText().strip(),
            status_map[self.status_input.currentText()],
            deadline,
        )

# ── Task Card Widget ──────────────────────────────────────────────────────────

class TaskCard(QFrame):
    """A single task displayed as a card with a delete button."""

    def __init__(self, task: dict, on_delete, parent=None):
        super().__init__(parent)
        self.task = task
        self.setStyleSheet(TASK_CARD_STYLE)
        self.setFrameShape(QFrame.StyledPanel)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(14, 10, 14, 10)
        outer.setSpacing(6)

        # ── Top row: title + delete button ──
        top_row = QHBoxLayout()
        top_row.setSpacing(8)

        title = QLabel(task.get("title", "Untitled"))
        title.setStyleSheet("color: #cdd6f4; font-size: 14px; font-weight: bold;")
        title.setWordWrap(True)
        top_row.addWidget(title, stretch=1)

        del_btn = QPushButton("✕")
        del_btn.setStyleSheet(DELETE_BTN_STYLE)
        del_btn.setFixedSize(28, 28)
        del_btn.setToolTip("Delete task")
        del_btn.clicked.connect(lambda: on_delete(task.get("id")))
        top_row.addWidget(del_btn, alignment=Qt.AlignTop)

        outer.addLayout(top_row)

        # ── Description ──
        desc = task.get("description", "")
        if desc:
            desc_label = QLabel(desc)
            desc_label.setStyleSheet("color: #a6adc8; font-size: 12px;")
            desc_label.setWordWrap(True)
            outer.addWidget(desc_label)

        # ── Date row: created + deadline ──
        date_row = QHBoxLayout()
        date_row.setSpacing(16)

        created = format_date(task.get("created_at", ""))
        if created:
            created_lbl = QLabel(f"📅 Added: {created}")
            created_lbl.setStyleSheet("color: #6c7086; font-size: 11px;")
            date_row.addWidget(created_lbl)

        deadline = format_date(task.get("deadline", ""))
        if deadline:
            deadline_lbl = QLabel(f"⏰ Due: {deadline}")
            deadline_lbl.setStyleSheet("color: #fab387; font-size: 11px; font-weight: bold;")
            date_row.addWidget(deadline_lbl)

        date_row.addStretch()
        outer.addLayout(date_row)

# ── Task Page (one per status) ────────────────────────────────────────────────

class TaskPage(QWidget):
    """Scrollable page showing all tasks for a given status."""

    def __init__(self, title: str, parent=None):
        super().__init__(parent)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 24, 24, 24)
        outer.setSpacing(16)

        heading = QLabel(title)
        heading.setStyleSheet("color: #cdd6f4; font-size: 22px; font-weight: bold;")
        outer.addWidget(heading)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.cards_widget = QWidget()
        self.cards_widget.setStyleSheet("background: transparent;")
        self.cards_layout = QVBoxLayout(self.cards_widget)
        self.cards_layout.setSpacing(10)
        self.cards_layout.setAlignment(Qt.AlignTop)

        self.empty_label = QLabel("No tasks here yet.")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setStyleSheet("color: #6c7086; font-size: 14px;")
        self.cards_layout.addWidget(self.empty_label)

        self.scroll.setWidget(self.cards_widget)
        outer.addWidget(self.scroll)

    def refresh(self, tasks: list[dict], on_delete) -> None:
        """Clear and re-render all task cards."""
        for i in reversed(range(self.cards_layout.count())):
            item = self.cards_layout.itemAt(i)
            widget = item.widget() if item else None
            if widget and widget is not self.empty_label:
                self.cards_layout.takeAt(i)
                widget.deleteLater()

        if not tasks:
            self.empty_label.show()
            return

        self.empty_label.hide()
        for task in tasks:
            self.cards_layout.addWidget(TaskCard(task, on_delete))

# ── Main Window ───────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Task Manager")
        self.setMinimumSize(900, 600)

        self.current_file = DEFAULT_PATH
        self.tasks: list[dict] = load_tasks(self.current_file)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        root_layout = QHBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ── Sidebar ──
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(210)
        sidebar.setStyleSheet(SIDEBAR_STYLE)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(12, 20, 12, 20)
        sidebar_layout.setSpacing(8)

        app_title = QLabel("📝 Tasks")
        app_title.setStyleSheet("color: #cdd6f4; font-size: 18px; font-weight: bold; padding: 8px 4px;")
        sidebar_layout.addWidget(app_title)
        sidebar_layout.addSpacing(12)

        self.nav_buttons = []
        nav_items = [("☐  To Do", 0), ("⟳  In Progress", 1), ("✓  Done", 2)]
        for label, index in nav_items:
            btn = QPushButton(label)
            btn.setStyleSheet(NAV_BUTTON_STYLE)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, i=index: self.switch_page(i))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        sidebar_layout.addStretch()

        load_btn = QPushButton("📂  Load JSON File")
        load_btn.setStyleSheet(LOAD_BUTTON_STYLE)
        load_btn.clicked.connect(self.on_load_file)
        sidebar_layout.addWidget(load_btn)

        sidebar_layout.addSpacing(6)

        add_btn = QPushButton("+ Add Task")
        add_btn.setStyleSheet(ADD_BUTTON_STYLE)
        add_btn.clicked.connect(self.on_add_task)
        sidebar_layout.addWidget(add_btn)

        # ── Content stack ──
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background-color: #181825;")

        status_keys = ["todo", "inprogress", "done"]
        page_titles = ["To Do", "In Progress", "Done"]
        self.pages: dict[str, TaskPage] = {}

        for key, title in zip(status_keys, page_titles):
            page = TaskPage(title)
            self.pages[key] = page
            self.stack.addWidget(page)

        root_layout.addWidget(sidebar)
        root_layout.addWidget(self.stack)

        self.switch_page(0)
        self.refresh_all_pages()

    # ── Navigation ────────────────────────────────────────────────────────────

    def switch_page(self, index: int) -> None:
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)

    # ── Refresh ───────────────────────────────────────────────────────────────

    def refresh_all_pages(self) -> None:
        for key, page in self.pages.items():
            page.refresh(get_tasks_by_status(self.tasks, key), self.on_delete_task)

    # ── Slots ─────────────────────────────────────────────────────────────────

    def on_add_task(self) -> None:
        dialog = AddTaskDialog(self)
        if dialog.exec() != QDialog.Accepted:
            return

        title, description, status, deadline = dialog.get_values()
        if not title:
            QMessageBox.warning(self, "Missing Title", "Please enter a task title.")
            return

        add_task(self.tasks, title, description, status, deadline)
        save_tasks(self.tasks, self.current_file)
        self.refresh_all_pages()

        page_index = {"todo": 0, "inprogress": 1, "done": 2}[status]
        self.switch_page(page_index)

    def on_delete_task(self, task_id: str) -> None:
        reply = QMessageBox.question(
            self, "Delete Task",
            "Are you sure you want to delete this task?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        delete_task(self.tasks, task_id)
        save_tasks(self.tasks, self.current_file)
        self.refresh_all_pages()

    def on_load_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Tasks JSON", "", "JSON Files (*.json)"
        )
        if not path:
            return
        self.tasks = load_tasks(Path(path))
        self.current_file = Path(path)
        self.refresh_all_pages()


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
