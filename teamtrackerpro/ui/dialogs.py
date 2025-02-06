import os
import logging
from datetime import datetime

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QStackedWidget, QFileDialog, QCheckBox, QTextEdit, QListWidget,
    QComboBox, QToolBar, QAction, QMessageBox, QWidget, QTabWidget,
    QApplication, QStyleFactory, QSizePolicy
)
from PyQt5.QtCore import Qt, QSize, QSettings, QTimer
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWebEngineWidgets import QWebEngineView
import markdown
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from teamtrackerpro.models.database_manager import DatabaseManager, AUDIT_NOTE_TYPES
from teamtrackerpro.models.email_generator import EmailGenerator
from teamtrackerpro.ui.base import ThemedDialog, ThemedWidget
from teamtrackerpro.ui.widgets import AnimatedButton, StyledLineEdit, StyledTextEdit, StyledComboBox
from teamtrackerpro.ui.themes import get_dark_palette, get_light_palette
from teamtrackerpro.utils.logo import get_logo_pixmap  # Import the logo function

UPLOADS_DIR = "uploads"


class EmployeeDetailsDialog(ThemedDialog):
    def __init__(self, employee, db_manager, dark_mode: bool, current_user: dict, parent=None):
        super().__init__(dark_mode, parent)
        self.employee = employee
        self.db_manager = db_manager
        self.current_user = current_user
        self.setWindowTitle("Employee Details")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        tabs = QTabWidget()

        # Notes Tab
        notes_tab = QWidget()
        notes_layout = QVBoxLayout(notes_tab)
        self.notes_table = QTableWidget(0, 4)
        self.notes_table.setHorizontalHeaderLabels(["Timestamp", "Note Type", "Note Preview", "Created By"])
        self.notes_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        notes_layout.addWidget(self.notes_table)
        self.load_notes(self.employee[0])
        tabs.addTab(notes_tab, "Notes")

        # KPIs Tab
        kpis_tab = QWidget()
        kpis_layout = QVBoxLayout(kpis_tab)
        self.kpis_table = QTableWidget(0, 5)
        self.kpis_table.setHorizontalHeaderLabels(["Timestamp", "Calls", "Tickets", "Sentiment", "Summary"])
        self.kpis_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        kpis_layout.addWidget(self.kpis_table)
        self.load_kpis(self.employee[0])
        tabs.addTab(kpis_tab, "KPIs")

        # Timestamps Tab (Example - Adapt as needed)
        timestamps_tab = QWidget()
        timestamps_layout = QVBoxLayout(timestamps_tab)
        self.timestamps_table = QTableWidget(0, 1)  # Example: Join Date
        self.timestamps_table.setHorizontalHeaderLabels(["Join Date"])
        self.timestamps_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        timestamps_layout.addWidget(self.timestamps_table)
        self.load_timestamps(self.employee[0])  # Load timestamps
        tabs.addTab(timestamps_tab, "Timestamps")

        layout.addWidget(tabs)
        close_btn = AnimatedButton("Close", self)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def load_notes(self, employee_id):
        self.notes_table.setRowCount(0)
        notes = self.db_manager.get_notes_for_employee(employee_id)
        for note in notes:
            row = self.notes_table.rowCount()
            self.notes_table.insertRow(row)
            self.notes_table.setItem(row, 0, QTableWidgetItem(note[0]))  # Timestamp
            self.notes_table.setItem(row, 1, QTableWidgetItem(note[1]))  # Note Type
            self.notes_table.setItem(row, 2, QTableWidgetItem(note[2][:50] + "..." if len(note[2]) > 50 else note[2]))  # Note Preview
            # Get username of the creator
            creator_id = note[3]
            creator = self.db_manager.get_user_by_id(creator_id)
            creator_username = creator[1] if creator else "Unknown"
            self.notes_table.setItem(row, 3, QTableWidgetItem(creator_username))  # Created By

    def load_kpis(self, employee_id):
        self.kpis_table.setRowCount(0)
        kpis = self.db_manager.get_kpis_for_employee(employee_id)
        for kpi in kpis:
            row = self.kpis_table.rowCount()
            self.kpis_table.insertRow(row)
            self.kpis_table.setItem(row, 0, QTableWidgetItem(kpi[0]))  # Timestamp
            self.kpis_table.setItem(row, 1, QTableWidgetItem(str(kpi[1])))  # Calls
            self.kpis_table.setItem(row, 2, QTableWidgetItem(str(kpi[2])))  # Tickets
            self.kpis_table.setItem(row, 3, QTableWidgetItem(str(kpi[3])))  # Sentiment
            self.kpis_table.setItem(row, 4, QTableWidgetItem(kpi[4]))  # Summary

    def load_timestamps(self, employee_id):
        join_date = self.employee[4]  # Get the join date from the employee data
        self.timestamps_table.setRowCount(0)
        row = self.timestamps_table.rowCount()
        self.timestamps_table.insertRow(row)
        self.timestamps_table.setItem(row, 0, QTableWidgetItem(join_date))


class AddEmployeeDialog(ThemedDialog):
    def __init__(self, db_manager, dark_mode: bool, parent=None):
        super().__init__(dark_mode, parent)
        self.db_manager = db_manager
        self.setWindowTitle("Add Employee")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        self.first_name_edit = StyledLineEdit(self)
        self.first_name_edit.setPlaceholderText("First Name")
        layout.addWidget(self.first_name_edit)

        self.last_name_edit = StyledLineEdit(self)
        self.last_name_edit.setPlaceholderText("Last Name")
        layout.addWidget(self.last_name_edit)

        self.email_edit = StyledLineEdit(self)
        self.email_edit.setPlaceholderText("Email")
        layout.addWidget(self.email_edit)

        self.join_date_edit = StyledLineEdit(self)
        self.join_date_edit.setPlaceholderText("Join Date (YYYY-MM-DD)")
        layout.addWidget(self.join_date_edit)

        btn_layout = QHBoxLayout()
        add_btn = AnimatedButton("Add Employee", self)
        add_btn.clicked.connect(self.add_employee)
        btn_layout.addWidget(add_btn)

        cancel_btn = AnimatedButton("Cancel", self)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def add_employee(self):
        first_name = self.first_name_edit.text().strip()
        last_name = self.last_name_edit.text().strip()
        email = self.email_edit.text().strip()
        join_date = self.join_date_edit.text().strip()

        if not first_name or not last_name or not email or not join_date:
            QMessageBox.warning(self, "Input Error", "All fields are required.")
            return

        try:
            # Assuming your db_manager has an add_employee method
            self.db_manager.add_employee(first_name, last_name, email, join_date)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return
        self.accept()


class EditEmployeeDialog(ThemedDialog):
    def __init__(self, employee, db_manager, dark_mode: bool, parent=None):
        super().__init__(dark_mode, parent)
        self.employee = employee  # Assuming employee is a tuple: (id, first_name, last_name, email, join_date)
        self.db_manager = db_manager
        self.setWindowTitle("Edit Employee")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        self.first_name_edit = StyledLineEdit(self)
        self.first_name_edit.setText(self.employee[1])
        layout.addWidget(self.first_name_edit)

        self.last_name_edit = StyledLineEdit(self)
        self.last_name_edit.setText(self.employee[2])
        layout.addWidget(self.last_name_edit)

        self.email_edit = StyledLineEdit(self)
        self.email_edit.setText(self.employee[3])
        layout.addWidget(self.email_edit)

        self.join_date_edit = StyledLineEdit(self)
        self.join_date_edit.setText(self.employee[4])
        layout.addWidget(self.join_date_edit)

        btn_layout = QHBoxLayout()
        save_btn = AnimatedButton("Save Changes", self)
        save_btn.clicked.connect(self.save_changes)
        btn_layout.addWidget(save_btn)

        cancel_btn = AnimatedButton("Cancel", self)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def save_changes(self):
        first_name = self.first_name_edit.text().strip()
        last_name = self.last_name_edit.text().strip()
        email = self.email_edit.text().strip()
        join_date = self.join_date_edit.text().strip()

        if not first_name or not last_name or not email or not join_date:
            QMessageBox.warning(self, "Input Error", "All fields are required.")
            return

        try:
            # Assuming your db_manager has an update_employee method
            self.db_manager.update_employee(self.employee[0], first_name, last_name, email, join_date)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return
        self.accept()


class AddNoteDialog(ThemedDialog):
    def __init__(self, employee_id, db_manager, dark_mode: bool, current_user, parent=None):
        super().__init__(dark_mode, parent)
        self.employee_id = employee_id
        self.db_manager = db_manager
        self.current_user = current_user
        self.setWindowTitle("Add Note")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Note Type:"))
        self.note_type_combo = StyledComboBox(self)
        for note_type in AUDIT_NOTE_TYPES:
            self.note_type_combo.addItem(note_type)
        layout.addWidget(self.note_type_combo)

        self.note_text_edit = StyledTextEdit(self)
        self.note_text_edit.setPlaceholderText("Enter note text here...")
        layout.addWidget(self.note_text_edit)

        btn_layout = QHBoxLayout()
        add_btn = AnimatedButton("Add Note", self)
        add_btn.clicked.connect(self.add_note)
        btn_layout.addWidget(add_btn)

        cancel_btn = AnimatedButton("Cancel", self)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def add_note(self):
        note_type = self.note_type_combo.currentText()
        note_text = self.note_text_edit.toPlainText().strip()

        if not note_text:
            QMessageBox.warning(self, "Input Error", "Note text cannot be empty.")
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            # Assuming your db_manager has an add_note method accepting these parameters
            self.db_manager.add_note(self.employee_id, note_type, note_text, self.current_user["id"], timestamp)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return
        self.accept()


class AddKpiDialog(ThemedDialog):
    def __init__(self, employee_id, db_manager, dark_mode: bool, parent=None):
        super().__init__(dark_mode, parent)
        self.employee_id = employee_id
        self.db_manager = db_manager
        self.setWindowTitle("Add KPI")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Calls:"))
        self.calls_edit = StyledLineEdit(self)
        self.calls_edit.setPlaceholderText("Calls")
        layout.addWidget(self.calls_edit)

        layout.addWidget(QLabel("Tickets:"))
        self.tickets_edit = StyledLineEdit(self)
        self.tickets_edit.setPlaceholderText("Tickets")
        layout.addWidget(self.tickets_edit)

        layout.addWidget(QLabel("Sentiment:"))
        self.sentiment_edit = StyledLineEdit(self)
        self.sentiment_edit.setPlaceholderText("Sentiment")
        layout.addWidget(self.sentiment_edit)

        layout.addWidget(QLabel("Summary:"))
        self.summary_edit = StyledLineEdit(self)
        self.summary_edit.setPlaceholderText("Summary")
        layout.addWidget(self.summary_edit)

        btn_layout = QHBoxLayout()
        add_btn = AnimatedButton("Add KPI", self)
        add_btn.clicked.connect(self.add_kpi)
        btn_layout.addWidget(add_btn)

        cancel_btn = AnimatedButton("Cancel", self)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def add_kpi(self):
        try:
            calls = int(self.calls_edit.text().strip())
            tickets = int(self.tickets_edit.text().strip())
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Calls and Tickets must be numeric.")
            return

        sentiment = self.sentiment_edit.text().strip()
        summary = self.summary_edit.text().strip()

        if not sentiment or not summary:
            QMessageBox.warning(self, "Input Error", "Sentiment and Summary cannot be empty.")
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            # Assuming your db_manager has an add_kpi method accepting these parameters
            self.db_manager.add_kpi(self.employee_id, timestamp, calls, tickets, sentiment, summary)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return
        self.accept()


class EmailDialog(ThemedDialog):
    def __init__(self, employee, db_manager, dark_mode: bool, parent=None):
        super().__init__(dark_mode, parent)
        self.employee = employee  # Assuming employee[3] contains the email address.
        self.db_manager = db_manager
        self.setWindowTitle("Send Email")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        self.to_label = QLabel(f"To: {self.employee[3]}")
        layout.addWidget(self.to_label)

        self.subject_edit = StyledLineEdit(self)
        self.subject_edit.setPlaceholderText("Subject")
        layout.addWidget(self.subject_edit)

        self.body_edit = StyledTextEdit(self)
        self.body_edit.setPlaceholderText("Email body...")
        layout.addWidget(self.body_edit)

        btn_layout = QHBoxLayout()
        send_btn = AnimatedButton("Send Email", self)
        send_btn.clicked.connect(self.send_email)
        btn_layout.addWidget(send_btn)

        cancel_btn = AnimatedButton("Cancel", self)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def send_email(self):
        subject = self.subject_edit.text().strip()
        body = self.body_edit.toPlainText().strip()

        if not subject or not body:
            QMessageBox.warning(self, "Input Error", "Subject and body cannot be empty.")
            return

        try:
            email_gen = EmailGenerator(self.db_manager)
            # Assuming EmailGenerator has a send_email method
            email_gen.send_email(self.employee[3], subject, body)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return
        self.accept()


class ExportDialog(ThemedDialog):
    def __init__(self, db_manager, dark_mode: bool, parent=None):
        super().__init__(dark_mode, parent)
        self.db_manager = db_manager
        self.setWindowTitle("Export Data")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        self.file_path_edit = StyledLineEdit(self)
        self.file_path_edit.setPlaceholderText("Select export file path...")
        layout.addWidget(self.file_path_edit)

        browse_btn = AnimatedButton("Browse", self)
        browse_btn.clicked.connect(self.browse_file)
        layout.addWidget(browse_btn)

        btn_layout = QHBoxLayout()
        export_btn = AnimatedButton("Export", self)
        export_btn.clicked.connect(self.export_data)
        btn_layout.addWidget(export_btn)

        cancel_btn = AnimatedButton("Cancel", self)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def browse_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Select Export File", "", "CSV Files (*.csv);;All Files (*)", options=options
        )
        if file_path:
            self.file_path_edit.setText(file_path)

    def export_data(self):
        file_path = self.file_path_edit.text().strip()
        if not file_path:
            QMessageBox.warning(self, "Input Error", "Please select a file path to export data.")
            return
        try:
            # Assuming your db_manager has an export_data method accepting a file path
            self.db_manager.export_data(file_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return
        self.accept()


class LoginDialog(ThemedDialog):
    def __init__(self, db_manager, dark_mode: bool, parent=None):
        super().__init__(dark_mode, parent)
        self.db_manager = db_manager
        self.setWindowTitle("Login")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        self.username_edit = StyledLineEdit(self)
        self.username_edit.setPlaceholderText("Username")
        layout.addWidget(self.username_edit)

        self.password_edit = StyledLineEdit(self)
        self.password_edit.setPlaceholderText("Password")
        self.password_edit.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_edit)

        btn_layout = QHBoxLayout()
        login_btn = AnimatedButton("Login", self)
        login_btn.clicked.connect(self.login)
        btn_layout.addWidget(login_btn)

        cancel_btn = AnimatedButton("Cancel", self)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def login(self):
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Input Error", "Please enter both username and password.")
            return

        try:
            # Assuming your db_manager has an authenticate_user method that returns a user dict or None
            user = self.db_manager.authenticate_user(username, password)
            if not user:
                QMessageBox.warning(self, "Login Failed", "Invalid username or password.")
                return
            self.user = user
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return
        self.accept()


class SettingsDialog(ThemedDialog):
    def __init__(self, settings: QSettings, parent=None):
        # Read dark_mode setting (default to False if not set)
        dark_mode = settings.value("dark_mode", False, type=bool)
        super().__init__(dark_mode, parent)
        self.settings = settings
        self.setWindowTitle("Settings")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        self.dark_mode_checkbox = QCheckBox("Enable Dark Mode")
        self.dark_mode_checkbox.setChecked(self.settings.value("dark_mode", False, type=bool))
        layout.addWidget(self.dark_mode_checkbox)

        # Add additional settings widgets here as needed

        btn_layout = QHBoxLayout()
        save_btn = AnimatedButton("Save Settings", self)
        save_btn.clicked.connect(self.save_settings)
        btn_layout.addWidget(save_btn)

        cancel_btn = AnimatedButton("Cancel", self)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def save_settings(self):
        self.settings.setValue("dark_mode", self.dark_mode_checkbox.isChecked())
        # Save additional settings as needed
        self.accept()


class Notification(ThemedDialog):
    def __init__(self, message, dark_mode, parent=None):
        super().__init__(dark_mode, parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setStyleSheet("""
            QDialog {
                background-color: #28a745; /* Green background */
                color: white;
                border-radius: 5px;
                padding: 10px;
            }
        """)

        layout = QVBoxLayout(self)
        label = QLabel(message)
        layout.addWidget(label)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.close)
        self.timer.start(3000)  # Close after 3 seconds

    def show(self):
        super().show()
        # Center the notification
        screen_geometry = QApplication.desktop().screenGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = screen_geometry.height() - self.height() - 100  # 100px from the bottom
        self.move(x, y)
