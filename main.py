import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QLabel, QPushButton
)
from PySide6.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Task Manager")
        self.setMinimumSize(800, 600)

        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(16)

        # Placeholder UI
        label = QLabel("📝 Task Manager")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 28px; font-weight: bold;")

        subtitle = QLabel("Your tasks will appear here.")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 14px; color: gray;")

        btn = QPushButton("+ Add Task")
        btn.setFixedWidth(160)
        btn.setStyleSheet("font-size: 14px; padding: 8px;")
        btn.clicked.connect(self.on_add_task)

        layout.addWidget(label)
        layout.addWidget(subtitle)
        layout.addWidget(btn, alignment=Qt.AlignCenter)

    def on_add_task(self):
        print("Add Task button clicked — logic coming soon!")


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()