import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QStackedWidget
)
from PySide6.QtCore import Qt


SIDEBAR_STYLE = """
    QWidget#sidebar {
        background-color: #1e1e2e;
    }
"""

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
    QPushButton:hover {
        background-color: #313244;
    }
    QPushButton:checked {
        background-color: #45475a;
        color: #cba6f7;
    }
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
    QPushButton:hover {
        background-color: #b4befe;
    }
"""


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Task Manager")
        self.setMinimumSize(900, 600)

        # Root layout: sidebar | content
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        root_layout = QHBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # --- Sidebar ---
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet(SIDEBAR_STYLE)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(12, 20, 12, 20)
        sidebar_layout.setSpacing(8)

        app_title = QLabel("📝 Tasks")
        app_title.setStyleSheet("color: #cdd6f4; font-size: 18px; font-weight: bold; padding: 8px 4px;")
        sidebar_layout.addWidget(app_title)
        sidebar_layout.addSpacing(12)

        # Nav buttons
        self.nav_buttons = []
        nav_items = [
            ("☐  To Do", 0),
            ("⟳  In Progress", 1),
            ("✓  Done", 2),
        ]
        for label, index in nav_items:
            btn = QPushButton(label)
            btn.setStyleSheet(NAV_BUTTON_STYLE)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, i=index: self.switch_page(i))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        sidebar_layout.addStretch()

        add_btn = QPushButton("+ Add Task")
        add_btn.setStyleSheet(ADD_BUTTON_STYLE)
        add_btn.clicked.connect(self.on_add_task)
        sidebar_layout.addWidget(add_btn)

        # --- Content area ---
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background-color: #181825;")

        for page_title in ["To Do", "In Progress", "Done"]:
            page = QWidget()
            page_layout = QVBoxLayout(page)
            page_layout.setAlignment(Qt.AlignCenter)

            title = QLabel(page_title)
            title.setAlignment(Qt.AlignCenter)
            title.setStyleSheet("color: #cdd6f4; font-size: 26px; font-weight: bold;")

            subtitle = QLabel("No tasks here yet.")
            subtitle.setAlignment(Qt.AlignCenter)
            subtitle.setStyleSheet("color: #6c7086; font-size: 14px;")

            page_layout.addWidget(title)
            page_layout.addSpacing(8)
            page_layout.addWidget(subtitle)
            self.stack.addWidget(page)

        root_layout.addWidget(sidebar)
        root_layout.addWidget(self.stack)

        # Select first page by default
        self.switch_page(0)

    def switch_page(self, index):
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)

    def on_add_task(self):
        print("Add Task clicked — logic coming soon!")


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
