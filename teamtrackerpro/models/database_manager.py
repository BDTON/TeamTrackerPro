import os
import sqlite3
import logging
from datetime import datetime
from typing import Any, List, Tuple, Optional

UPLOADS_DIR = "uploads"
if not os.path.exists(UPLOADS_DIR):
    os.makedirs(UPLOADS_DIR)

AUDIT_NOTE_TYPES = {"Ticket Audit", "Call Audit"}

class DatabaseManager:
    def __init__(self, db_name="teamtracker.db"):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self._create_tables()

    def _create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,  -- Store securely (hashed)
                email TEXT UNIQUE,
                role TEXT NOT NULL DEFAULT 'employee' -- 'employee', 'team_leader', 'admin'
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                role TEXT NOT NULL DEFAULT 'employee', -- 'employee', 'team_leader'
                join_date TEXT,
                last_audit_report TEXT,
                info TEXT
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER,
                timestamp TEXT,
                note_type TEXT,
                note TEXT,
                created_by INTEGER,  -- ID of the user who created the note
                FOREIGN KEY (employee_id) REFERENCES employees(id),
                FOREIGN KEY (created_by) REFERENCES users(id)
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER,
                timestamp TEXT,
                calls_handled INTEGER,
                tickets_triaged INTEGER,
                sentiment_score REAL,
                summary TEXT,
                FOREIGN KEY (employee_id) REFERENCES employees(id)
            )
        """)

        self.connection.commit()

    # User Management
    def add_user(self, username, password, email, role):  # Password should be hashed
        try:
            self.cursor.execute("INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)", (username, password, email, role))
            self.connection.commit()
            return True
        except sqlite3.IntegrityError: # username already exists
            return False

    def get_user_by_username(self, username: str) -> Optional[Tuple[Any, ...]]:
        self.cursor.execute("SELECT id, username, password, email, role FROM users WHERE username = ?", (username,))
        return self.cursor.fetchone()

    def get_user_by_id(self, user_id: int) -> Optional[Tuple[Any, ...]]:
        self.cursor.execute("SELECT id, username, email, role FROM users WHERE id = ?", (user_id,))
        return self.cursor.fetchone()

    # Employee Management
    def add_employee(self, name, email, role, join_date, info):
        try:
            self.cursor.execute("INSERT INTO employees (name, email, role, join_date, info) VALUES (?, ?, ?, ?, ?)", (name, email, role, join_date, info))
            self.connection.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_employees(self) -> List[Tuple[Any, ...]]:
        self.cursor.execute("SELECT id, name, email, role, join_date, last_audit_report, info FROM employees")
        return self.cursor.fetchall()

    def update_employee(self, employee_id, name, email, role, join_date, info):
        self.cursor.execute("""
            UPDATE employees SET name=?, email=?, role=?, join_date=?, info=? WHERE id=?
        """, (name, email, role, join_date, info, employee_id))
        self.connection.commit()

    def delete_employee(self, employee_id):
        self.cursor.execute("DELETE FROM employees WHERE id=?", (employee_id,))
        self.connection.commit()

    def get_employee_by_id(self, employee_id: int) -> Optional[Tuple[Any, ...]]:
        self.cursor.execute("SELECT id, name, email, role, join_date, last_audit_report, info FROM employees WHERE id = ?", (employee_id,))
        return self.cursor.fetchone()

    # Notes Management
    def add_note(self, employee_id, note_type, note, created_by):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("INSERT INTO notes (employee_id, timestamp, note_type, note, created_by) VALUES (?, ?, ?, ?, ?)", (employee_id, timestamp, note_type, note, created_by))
        self.connection.commit()

    def get_notes_for_employee(self, employee_id: int) -> List[Tuple[Any, ...]]:
        self.cursor.execute("SELECT timestamp, note_type, note, created_by FROM notes WHERE employee_id = ? ORDER BY timestamp DESC", (employee_id,))
        return self.cursor.fetchall()

    # Performance Data (KPIs)
    def add_kpi(self, employee_id, calls, tickets, sentiment, summary):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("INSERT INTO performance (employee_id, timestamp, calls_handled, tickets_triaged, sentiment_score, summary) VALUES (?, ?, ?, ?, ?, ?)", (employee_id, timestamp, calls, tickets, sentiment, summary))
        self.connection.commit()

    def get_kpis_for_employee(self, employee_id: int) -> List[Tuple[Any, ...]]:
        self.cursor.execute("SELECT timestamp, calls_handled, tickets_triaged, sentiment_score, summary FROM performance WHERE employee_id = ? ORDER BY timestamp DESC", (employee_id,))
        return self.cursor.fetchall()

    def close(self) -> None:
        self.connection.close()
        logging.info("Database connection closed.")