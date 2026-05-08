import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QStackedWidget, QDialog,
    QLineEdit, QTextEdit, QComboBox,
    QFileDialog, QScrollArea, QFrame,
    QMessageBox, QDateEdit, QCheckBox,
    QRadioButton, QButtonGroup
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

# Status badge colors and labels
STATUS_META = {
    "todo":       {"label": "☐ To Do",       "bg": "#45475a", "color": "#cdd6f4"},
    "inprogress": {"label": "⟳ In Progress",  "bg": "#1e3a5f", "color": "#89b4fa"},
    "done":       {"label": "✓ Done",         "bg": "#1e3a2f", "color": "#a6e3a1"},
}

def status_badge_style(status: str) -> str:
    meta = STATUS_META.get(status, STATUS_META["todo"])
    return f"""
        QPushButton {{
            background-color: {meta['bg']};
            color: {meta['color']};
            font-size: 11px;
            font-weight: bold;
            padding: 3px 10px;
            border: none;
            border-radius: 10px;
        }}
        QPushButton:hover {{
            border: 1px solid {meta['color']};
        }}
    """

# ── Add Task Dialog ───────────────────────────────────────────────────────────

class AddTaskDialog(QDialog):
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
        deadline_row = QHBoxLayout()
        self.deadline_input = QDateEdit()
        self.deadline_input.setCalendarPopup(True)
        self.deadline_input.setDate(QDate.currentDate())
        self.deadline_input.setStyleSheet(INPUT_STYLE)
        self.deadline_input.setDisplayFormat("dd MMM yyyy")

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

    @staticmethod
    def _label(text: str) -> QLabel:
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

# ── Edit Task Dialog ──────────────────────────────────────────────────────────

RADIO_STYLE = """
    QRadioButton {{
        color: {color};
        font-size: 13px;
        font-weight: bold;
        spacing: 8px;
        padding: 8px 12px;
        border-radius: 8px;
        background-color: {bg};
    }}
    QRadioButton::indicator {{
        width: 0px;
        height: 0px;
    }}
    QRadioButton:checked {{
        border: 2px solid {color};
    }}
    QRadioButton:hover {{
        background-color: {hover};
    }}
"""

class EditTaskDialog(QDialog):
    """Dialog for editing task status and deadline."""

    def __init__(self, task: dict, parent=None):
        super().__init__(parent)
        self.task = task
        self.setWindowTitle("Edit Task")
        self.setMinimumWidth(380)
        self.setStyleSheet("background-color: #1e1e2e; color: #cdd6f4;")

        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(24, 24, 24, 24)

        # ── Task title (read-only header) ──
        title_lbl = QLabel(task.get("title", "Untitled"))
        title_lbl.setStyleSheet(
            "color: #cdd6f4; font-size: 15px; font-weight: bold;"
            "padding-bottom: 4px; border-bottom: 1px solid #45475a;"
        )
        title_lbl.setWordWrap(True)
        layout.addWidget(title_lbl)

        # ── Status section ──
        layout.addWidget(self._label("Status"))

        self.status_group = QButtonGroup(self)
        current_status = task.get("status", "todo")

        status_items = [
            ("todo",       "☐  To Do",       "#cdd6f4", "#45475a", "#585b70"),
            ("inprogress", "⟳  In Progress",  "#89b4fa", "#1e3a5f", "#1a2f4a"),
            ("done",       "✓  Done",         "#a6e3a1", "#1e3a2f", "#1a3028"),
        ]

        for value, label, color, bg, hover in status_items:
            rb = QRadioButton(label)
            rb.setProperty("status_value", value)
            rb.setChecked(value == current_status)
            rb.setStyleSheet(
                RADIO_STYLE.format(color=color, bg=bg, hover=hover)
            )
            self.status_group.addButton(rb)
            layout.addWidget(rb)

        # ── Deadline section ──
        layout.addSpacing(4)
        layout.addWidget(self._label("Deadline"))

        deadline_row = QHBoxLayout()
        self.deadline_input = QDateEdit()
        self.deadline_input.setCalendarPopup(True)
        self.deadline_input.setDisplayFormat("dd MMM yyyy")
        self.deadline_input.setStyleSheet(INPUT_STYLE)

        existing_deadline = task.get("deadline", "")
        if existing_deadline:
            d = QDate.fromString(existing_deadline, "yyyy-MM-dd")
            self.deadline_input.setDate(d if d.isValid() else QDate.currentDate())
        else:
            self.deadline_input.setDate(QDate.currentDate())

        self.no_deadline_cb = QCheckBox("No deadline")
        self.no_deadline_cb.setStyleSheet(CHECKBOX_STYLE)
        has_deadline = bool(existing_deadline)
        self.no_deadline_cb.setChecked(not has_deadline)
        self.deadline_input.setEnabled(has_deadline)
        self.no_deadline_cb.toggled.connect(
            lambda checked: self.deadline_input.setEnabled(not checked)
        )

        deadline_row.addWidget(self.deadline_input)
        deadline_row.addWidget(self.no_deadline_cb)
        layout.addLayout(deadline_row)

        # ── Save button ──
        layout.addSpacing(8)
        save_btn = QPushButton("Save Changes")
        save_btn.setStyleSheet(DIALOG_BTN_STYLE)
        save_btn.clicked.connect(self.accept)
        layout.addWidget(save_btn)

    @staticmethod
    def _label(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet("color: #a6adc8; font-size: 12px; font-weight: bold;")
        return lbl

    def get_values(self) -> tuple[str, str]:
        """Returns (new_status, new_deadline)."""
        selected = self.status_group.checkedButton()
        new_status = selected.property("status_value") if selected else self.task.get("status", "todo")
        deadline = ""
        if not self.no_deadline_cb.isChecked():
            deadline = self.deadline_input.date().toString("yyyy-MM-dd")
        return new_status, deadline


# ── Task Card Widget ──────────────────────────────────────────────────────────

class TaskCard(QFrame):
    """A single task card with delete button and a status badge that opens an edit dialog."""

    def __init__(self, task: dict, on_delete, on_edit, parent=None):
        super().__init__(parent)
        self.task = task
        self.on_edit = on_edit
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

        # ── Bottom row: dates + status badge ──
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(16)

        created = format_date(task.get("created_at", ""))
        if created:
            created_lbl = QLabel(f"📅 Added: {created}")
            created_lbl.setStyleSheet("color: #6c7086; font-size: 11px;")
            bottom_row.addWidget(created_lbl)

        deadline = format_date(task.get("deadline", ""))
        if deadline:
            deadline_lbl = QLabel(f"⏰ Due: {deadline}")
            deadline_lbl.setStyleSheet("color: #fab387; font-size: 11px; font-weight: bold;")
            bottom_row.addWidget(deadline_lbl)

        bottom_row.addStretch()

        # ── Status badge → opens EditTaskDialog ──
        current_status = task.get("status", "todo")
        meta = STATUS_META.get(current_status, STATUS_META["todo"])

        self.status_btn = QPushButton(meta["label"])
        self.status_btn.setStyleSheet(status_badge_style(current_status))
        self.status_btn.setToolTip("Edit status / deadline")
        self.status_btn.setCursor(Qt.PointingHandCursor)
        self.status_btn.clicked.connect(self._open_edit_dialog)
        bottom_row.addWidget(self.status_btn)

        outer.addLayout(bottom_row)

    def _open_edit_dialog(self) -> None:
        dialog = EditTaskDialog(self.task, parent=self.window())
        if dialog.exec() == QDialog.Accepted:
            new_status, new_deadline = dialog.get_values()
            self.on_edit(self.task.get("id"), new_status, new_deadline)


# ── Task Page (one per status) ────────────────────────────────────────────────

class TaskPage(QWidget):
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

    def refresh(self, tasks: list[dict], on_delete, on_edit) -> None:
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
            self.cards_layout.addWidget(TaskCard(task, on_delete, on_edit))

# ── Schedule Page ─────────────────────────────────────────────────────────────

SCHEDULE_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
SCHEDULE_HOURS = [
    "08:00–09:00", "09:00–10:00", "10:00–11:00",
    "11:00–12:00", "12:00–13:00", "13:00–14:00",
    "14:00–15:00", "15:00–16:00", "16:00–17:00",
    "17:00–18:00", "18:00–19:00", "19:00–20:00"
]

SCHEDULE_CELL_STYLE = """
    QFrame {
        background-color: #313244;
        border-radius: 6px;
        border: 1px solid #45475a;
    }
"""

SCHEDULE_TASK_CHIP_STYLE = """
    QLabel {
        background-color: #45475a;
        color: #cdd6f4;
        border-radius: 4px;
        padding: 3px 6px;
        font-size: 11px;
    }
"""

SCHEDULE_DROP_LABEL_STYLE = "color: #6c7086; font-size: 11px; font-style: italic;"

class ScheduleCell(QFrame):
    """One time-slot cell for a given day."""

    def __init__(self, day: str, hour: str, save_callback=None, parent=None):
        super().__init__(parent)
        self.day = day
        self.hour = hour
        self._save_callback = save_callback
        self.setStyleSheet(SCHEDULE_CELL_STYLE)
        self.setFixedSize(150, 80)
        self.setAcceptDrops(True)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(6, 4, 6, 4)
        self._layout.setSpacing(3)
        self._layout.setAlignment(Qt.AlignTop)

        self._drop_hint = QLabel("drop here")
        self._drop_hint.setStyleSheet(SCHEDULE_DROP_LABEL_STYLE)
        self._layout.addWidget(self._drop_hint)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            self.setStyleSheet(SCHEDULE_CELL_STYLE.replace("#313244", "#3d3f57"))
            event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        self.setStyleSheet(SCHEDULE_CELL_STYLE)
        event.accept()

    def dropEvent(self, event):
        self.setStyleSheet(SCHEDULE_CELL_STYLE)
        data = event.mimeData().text()
        if "||" in data:
            title, bg, color = data.split("||")
        else:
            title, bg, color = data, "#cba6f7", "#1e1e2e"
        self._add_chip(title, bg, color)
        event.acceptProposedAction()
        if self._save_callback:
            self._save_callback()

    def _add_chip(self, title: str, bg: str = "#cba6f7", color: str = "#1e1e2e"):
        self._drop_hint.hide()

        container = QFrame()
        container.setStyleSheet(f"""
            QFrame {{
                background-color: {bg};
                border-radius: 4px;
            }}
        """)
        container.setProperty("chip_bg", bg)
        container.setProperty("chip_fg", color)
        container.setProperty("chip_title", title)

        row = QHBoxLayout(container)
        row.setContentsMargins(6, 4, 4, 4)
        row.setSpacing(4)

        chip = QLabel(title)
        chip.setStyleSheet(f"color: {color}; font-size: 11px; font-weight: bold; background: transparent;")
        chip.setWordWrap(True)
        chip.setAlignment(Qt.AlignCenter)
        row.addWidget(chip, stretch=1)

        remove_btn = QPushButton("✕")
        remove_btn.setFixedSize(16, 16)
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: rgba(255,255,255,0.6);
                border: none;
                font-size: 10px;
                padding: 0px;
            }
            QPushButton:hover { color: white; }
        """)
        remove_btn.clicked.connect(lambda: self._remove_chip(container))
        row.addWidget(remove_btn, alignment=Qt.AlignTop)

        self._layout.addWidget(container, stretch=1)

    def _remove_chip(self, container: QFrame) -> None:
        # count BEFORE removing
        remaining = [
            self._layout.itemAt(i).widget()
            for i in range(self._layout.count())
            if self._layout.itemAt(i).widget() not in (None, self._drop_hint, container)
        ]
        self._layout.removeWidget(container)
        container.deleteLater()
        if not remaining:
            self._drop_hint.show()
        if self._save_callback:
            self._save_callback()


class DraggableTaskItem(QLabel):
    """A draggable task pill shown in the left panel of SchedulePage."""

    def __init__(self, title: str, bg: str = "#45475a", fg: str = "#cdd6f4", parent=None):
        super().__init__(title, parent)
        self._bg = bg
        self._fg = fg
        self._drag_start = None
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {bg};
                color: {fg};
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 12px;
                font-weight: bold;
            }}
            QLabel:hover {{ background-color: #585b70; }}
        """)
        self.setWordWrap(True)
        self.setCursor(Qt.OpenHandCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_start = event.position().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            from PySide6.QtGui import QDrag
            from PySide6.QtCore import QMimeData
            drag = QDrag(self)
            mime = QMimeData()
            mime.setText(f"{self.text()}||{self._bg}||{self._fg}")
            drag.setMimeData(mime)
            drag.exec(Qt.CopyAction)


class SchedulePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._cells: dict[tuple, ScheduleCell] = {}

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Left panel: To Do + In Progress tasks ──
        left = QWidget()
        left.setFixedWidth(180)
        left.setStyleSheet("background-color: #1e1e2e;")
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(12, 20, 12, 12)
        left_layout.setSpacing(8)

        lbl = QLabel("☐ To Do")
        lbl.setStyleSheet("color: #cba6f7; font-size: 13px; font-weight: bold;")
        left_layout.addWidget(lbl)

        hint = QLabel("Drag tasks →")
        hint.setStyleSheet("color: #6c7086; font-size: 11px;")
        left_layout.addWidget(hint)
        left_layout.addSpacing(6)

        self.task_list_layout = QVBoxLayout()
        self.task_list_layout.setSpacing(6)
        left_layout.addLayout(self.task_list_layout)

        left_layout.addSpacing(12)

        lbl2 = QLabel("⟳ In Progress")
        lbl2.setStyleSheet("color: #89b4fa; font-size: 13px; font-weight: bold;")
        left_layout.addWidget(lbl2)

        hint2 = QLabel("Drag tasks →")
        hint2.setStyleSheet("color: #6c7086; font-size: 11px;")
        left_layout.addWidget(hint2)
        left_layout.addSpacing(6)

        self.inprogress_list_layout = QVBoxLayout()
        self.inprogress_list_layout.setSpacing(6)
        left_layout.addLayout(self.inprogress_list_layout)
        left_layout.addStretch()

        root.addWidget(left)

        # ── Right panel: grid ──
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setStyleSheet("QScrollArea { border: none; background: #181825; }")

        grid_widget = QWidget()
        grid_widget.setStyleSheet("background: #181825;")
        from PySide6.QtWidgets import QGridLayout
        grid = QGridLayout(grid_widget)
        grid.setSpacing(4)
        grid.setContentsMargins(12, 20, 12, 20)

        # Header row
        time_header = QLabel("Time")
        time_header.setStyleSheet("color: #6c7086; font-size: 11px; font-weight: bold;")
        time_header.setAlignment(Qt.AlignCenter)
        grid.addWidget(time_header, 0, 0)

        for col, day in enumerate(SCHEDULE_DAYS, start=1):
            h = QLabel(day)
            h.setAlignment(Qt.AlignCenter)
            h.setFixedWidth(150)
            h.setStyleSheet("color: #cdd6f4; font-size: 12px; font-weight: bold; padding: 4px;")
            grid.addWidget(h, 0, col)
            grid.setColumnStretch(col, 0)

            # Time rows + cells
        for row, hour in enumerate(SCHEDULE_HOURS, start=1):
            time_lbl = QLabel(hour)
            time_lbl.setAlignment(Qt.AlignCenter)
            time_lbl.setStyleSheet("color: #6c7086; font-size: 10px;")
            time_lbl.setFixedWidth(70)
            grid.addWidget(time_lbl, row, 0)
            grid.setRowStretch(row, 0)

            for col, day in enumerate(SCHEDULE_DAYS, start=1):
                cell = ScheduleCell(day, hour, save_callback=self.save)
                self._cells[(day, hour)] = cell
                grid.addWidget(cell, row, col)

        right_scroll.setWidget(grid_widget)
        root.addWidget(right_scroll)
        self.load()

    SCHEDULE_SAVE_PATH = Path("data/schedule.json")

    def save(self) -> None:
        import json
        data = {}
        for (day, hour), cell in self._cells.items():
            titles = []
            for i in range(cell._layout.count()):
                widget = cell._layout.itemAt(i).widget()
                if isinstance(widget, QFrame):
                    bg = widget.property("chip_bg") or "#cba6f7"
                    fg = widget.property("chip_fg") or "#1e1e2e"
                    title = widget.property("chip_title") or ""
                    if title:
                        titles.append(f"{title}||{bg}||{fg}")
            if titles:
                data[f"{day}|{hour}"] = titles
        self.SCHEDULE_SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.SCHEDULE_SAVE_PATH.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    def load(self) -> None:
        import json
        if not self.SCHEDULE_SAVE_PATH.exists():
            return
        try:
            data = json.loads(self.SCHEDULE_SAVE_PATH.read_text(encoding="utf-8"))
        except Exception:
            return
        for key, titles in data.items():
            day, hour = key.split("|", 1)
            cell = self._cells.get((day, hour))
            if cell:
                for entry in titles:
                    if "||" in entry:
                        t, b, c = entry.split("||")
                        cell._add_chip(t, b, c)
                    else:
                        cell._add_chip(entry)

    def remove_task_chips(self, title: str) -> None:
        """Remove all chips with this title from every cell and save."""
        for cell in self._cells.values():
            for i in reversed(range(cell._layout.count())):
                widget = cell._layout.itemAt(i).widget()
                if widget is not None and widget is not cell._drop_hint and widget.property("chip_title") == title:
                    cell._layout.takeAt(i)
                    widget.deleteLater()
            # check remaining after removal
            remaining = [
                cell._layout.itemAt(i).widget()
                for i in range(cell._layout.count())
                if cell._layout.itemAt(i).widget() not in (None, cell._drop_hint)
            ]
            if not remaining:
                cell._drop_hint.show()
        self.save()

    def refresh_tasks(self, todo_tasks: list[dict], inprogress_tasks: list[dict] = None) -> None:
        """Repopulate the left panel with current To Do and In Progress tasks."""
        while self.task_list_layout.count():
            item = self.task_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for task in todo_tasks:
            pill = DraggableTaskItem(task.get("title", "Untitled"))
            self.task_list_layout.addWidget(pill)

        while self.inprogress_list_layout.count():
            item = self.inprogress_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for task in (inprogress_tasks or []):
            pill = DraggableTaskItem(task.get("title", "Untitled"), bg="#1e3a5f", fg="#89b4fa")
            self.inprogress_list_layout.addWidget(pill)

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
        nav_items = [("☐  To Do", 0), ("⟳  In Progress", 1), ("✓  Done", 2), ("📆 Schedule", 3)]
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

        # ── Schedule page (index 3) ──
        self.schedule_page = SchedulePage()
        self.stack.addWidget(self.schedule_page)

        root_layout.addWidget(sidebar)
        root_layout.addWidget(self.stack)

        self.switch_page(0)
        self.refresh_all_pages()

    def switch_page(self, index: int) -> None:
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)

    def refresh_all_pages(self) -> None:
        for key, page in self.pages.items():
            page.refresh(
                get_tasks_by_status(self.tasks, key),
                self.on_delete_task,
                self.on_edit_task,
            )
        self.schedule_page.refresh_tasks(
            get_tasks_by_status(self.tasks, "todo"),
            get_tasks_by_status(self.tasks, "inprogress"),
        )

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
        # find title before deleting so we can remove it from schedule
        title = next((t.get("title") for t in self.tasks if t.get("id") == task_id), None)
        delete_task(self.tasks, task_id)
        save_tasks(self.tasks, self.current_file)
        if title:
            self.schedule_page.remove_task_chips(title)
        self.refresh_all_pages()

    def on_edit_task(self, task_id: str, new_status: str, new_deadline: str) -> None:
        """Update a task's status and deadline, then refresh all pages."""
        for task in self.tasks:
            if task.get("id") == task_id:
                task["status"] = new_status
                task["deadline"] = new_deadline
                break
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
