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
        self.load_timestamps(self.employee[0]) # Load timestamps
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
        join_date = self.employee[4] # Get the join date from the employee data
        self.timestamps_table.setRowCount(0)
        row = self.timestamps_table.rowCount()
        self.timestamps_table.insertRow(row)
        self.timestamps_table.setItem(row, 0, QTableWidgetItem(join_date))

"""TODO: implement these classes so we stop getting errors.
class AddEmployeeDialog(ThemedDialog):
    def __init__(self, db_manager, dark_mode: bool, parent=None):
        super.__init__
        # ... (same as before)

class EditEmployeeDialog(ThemedDialog):
    def __init__(self, employee, db_manager, dark_mode: bool, parent=None):
        # ... (same as before)

class AddNoteDialog(ThemedDialog):
    def __init__(self, employee_id, db_manager, dark_mode: bool, current_user, parent=None):
        # ... (same as before)

class AddKpiDialog(ThemedDialog):
    def __init__(self, employee_id, db_manager, dark_mode: bool, parent=None):
        # ... (same as before)

class EmailDialog(ThemedDialog):
    def __init__(self, employee, db_manager, dark_mode: bool, parent=None):
        # ... (same as before)

class ExportDialog(ThemedDialog):
    def __init__(self, db_manager, dark_mode: bool, parent=None):
        # ... (same as before)

class LoginDialog(ThemedDialog):
    def __init__(self, db_manager, dark_mode: bool, parent=None):
        # ... (same as before)

class SettingsDialog(ThemedDialog):
    def __init__(self, settings, parent=None):
        # ... (same as before)
"""
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