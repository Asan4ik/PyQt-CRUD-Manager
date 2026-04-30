# PyQt-CRUD-Manager

A desktop **To-Do Task Manager** built with Python and PySide6 for the *Introduction to Programming 2* course at Astana IT University.

---

## Description

PyQt-CRUD-Manager is a GUI desktop application that lets users create, view, update, and delete personal tasks. All tasks are persisted locally using JSON files, so your data survives between sessions. The app is structured with a clean separation between UI logic and business logic, following OOP principles taught in the course.

---

## Features

- **Create** new tasks with a title, description, priority, and due date
- **Read** and browse all tasks in a sortable list view
- **Update** any task's details inline
- **Delete** tasks individually or in bulk
- **Data Persistence** — tasks are saved to a local JSON file automatically
- **Multi-tab / Multi-window GUI** built with PySide6
- **Exception handling** to prevent crashes on bad input or missing files
- **Modular codebase** — UI and business logic are separated into distinct modules

---

## Technologies Used

| Technology | Purpose |
|---|---|
| Python 3.10+ | Core language |
| PySide6 | Desktop GUI framework |
| JSON | Local data persistence |
| unittest | Unit testing |

---

## Project Structure

```
PyQt-CRUD-Manager/
├── main.py              # Entry point — launches the application
├── requirements.txt     # Project dependencies
├── README.md
├── data/
│   └── tasks.json       # Persisted task data (auto-created on first run)
├── utils/
│   ├── __init__.py
│   └── task_manager.py  # Business logic — CRUD operations, file I/O
└── tests/
    └── test_task_manager.py  # Unit tests for core logic
```

---

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/<your-username>/PyQt-CRUD-Manager.git
   cd PyQt-CRUD-Manager
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS / Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

---

## How to Run

```bash
python main.py
```

To run the unit tests:
```bash
python -m unittest discover tests/
```

---

## Screenshots

> *(Screenshots of the app will be here once the UI is complete)*

---

## Team Members

| Name | Role |
|---|---|
| Asanali Serik | *(TBD)* |
| Sanzhar Zhussip | *(TBD)* |
| Allazhar Kuat | *(TBD)* |

---

## Course Info

**Course:** Introduction to Programming 2  
**Department:** Software Engineering — Astana IT University  
**Instructor:** Assel Alimzhan