import os
import sys
import csv
import shutil
import logging
from datetime import datetime

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QStackedWidget, QFileDialog, QCheckBox, QDialog, QTextEdit, QListWidget,
    QComboBox, QToolBar, QAction, QMessageBox, QSizePolicy, QGridLayout
)
from PyQt5.QtCore import Qt, QSize, QSettings
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWebEngineWidgets import QWebEngineView
import markdown
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from teamtrackerpro.models.database_manager import DatabaseManager, AUDIT_NOTE_TYPES
from teamtrackerpro.models.email_generator import EmailGenerator
from teamtrackerpro.ui.dialogs import (
    EmployeeDetailsDialog, AddEmployeeDialog, EditEmployeeDialog, AddNoteDialog,
    AddKpiDialog, EmailDialog, ExportDialog, LoginDialog, SettingsDialog, Notification
)
from teamtrackerpro.ui.base import ThemedWidget
from teamtrackerpro.ui.widgets import AnimatedButton, StyledLineEdit, StyledTextEdit, StyledComboBox
from teamtrackerpro.ui.themes import get_dark_palette, get_light_palette
from teamtrackerpro.utils.logo import get_logo_pixmap  # Import the logo function

UPLOADS_DIR = "uploads"

class EmployeeManagerUI(ThemedWidget):
    def __init__(self, current_user, parent=None):
        super().__init__(self.is_dark_mode(), parent) # Initialize with current theme mode
        self.current_user = current_user
        self.db_manager = DatabaseManager()
        self.settings = QSettings("MyCompany", "TeamTrackerPro")
        self.setWindowTitle("TeamTrackerPro")
        self.setWindowIcon(QIcon("teamtrackerpro/resources/icons/app_icon.png")) # Set window icon
        self.init_ui()
        self.load_employees()

    def is_dark_mode(self):
        return self.settings.value("dark_mode", False, type=bool)

    def init_ui(self):
        # Apply theme based on settings
        if self.is_dark_mode():
            self.setStyleSheet("")  # Let individual widgets handle styling
            self.setPalette(get_dark_palette())
        else:
            self.setStyleSheet("")  # Let individual widgets handle styling
            self.setPalette(get_light_palette())


        main_layout = QVBoxLayout(self)

        # Toolbar
        toolbar = QToolBar(self)
        add_employee_action = QAction(QIcon("teamtrackerpro/resources/icons/add_employee.png"), "Add Employee", self) # Add employee icon
        add_employee_action.triggered.connect(self.show_add_employee_dialog)
        toolbar.addAction(add_employee_action)

        edit_employee_action = QAction(QIcon("teamtrackerpro/resources/icons/edit_employee.png"), "Edit Employee", self) # Edit employee icon
        edit_employee_action.triggered.connect(self.show_edit_employee_dialog)
        toolbar.addAction(edit_employee_action)

        delete_employee_action = QAction(QIcon("teamtrackerpro/resources/icons/delete_employee.png"), "Delete Employee", self) # Delete employee icon
        delete_employee_action.triggered.connect(self.delete_selected_employee)
        toolbar.addAction(delete_employee_action)

        add_note_action = QAction(QIcon("teamtrackerpro/resources/icons/add_note.png"), "Add Note", self) # Add note icon
        add_note_action.triggered.connect(self.show_add_note_dialog)
        toolbar.addAction(add_note_action)

        add_kpi_action = QAction(QIcon("teamtrackerpro/resources/icons/add_kpi.png"), "Add KPI", self) # Add KPI icon
        add_kpi_action.triggered.connect(self.show_add_kpi_dialog)
        toolbar.addAction(add_kpi_action)

        email_action = QAction(QIcon("teamtrackerpro/resources/icons/email.png"), "Email Follow-up", self) # Email icon
        email_action.triggered.connect(self.show_email_dialog)
        toolbar.addAction(email_action)

        export_action = QAction(QIcon("teamtrackerpro/resources/icons/export.png"), "Export Data", self) # Export icon
        export_action.triggered.connect(self.show_export_dialog)
        toolbar.addAction(export_action)

        settings_action = QAction(QIcon("teamtrackerpro/resources/icons/settings.png"), "Settings", self) # Settings icon
        settings_action.triggered.connect(self.show_settings_dialog)
        toolbar.addAction(settings_action)

        toolbar.setMovable(False)  # Prevent toolbar from being dragged around
        main_layout.addWidget(toolbar)

        # Employee Table
        self.employee_table = QTableWidget(0, 6)  # 6 columns
        self.employee_table.setHorizontalHeaderLabels([
            "ID", "Name", "Email", "Role", "Join Date", "Info"
        ])
        self.employee_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.employee_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.employee_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Make table read-only
        self.employee_table.doubleClicked.connect(self.show_employee_details) # Double click to open details
        main_layout.addWidget(self.employee_table)

        # Search Bar
        search_layout = QHBoxLayout()
        self.search_bar = StyledLineEdit(self)
        self.search_bar.textChanged.connect(self.filter_employees)
        search_layout.addWidget(QLabel("Search:"))
        search_layout.addWidget(self.search_bar)
        main_layout.addLayout(search_layout)

        # Logo (bottom-left corner)
        logo_pixmap = get_logo_pixmap(self.is_dark_mode())  # Get the logo pixmap
        if logo_pixmap:
            self.logo_label = QLabel(self)
            self.logo_label.setPixmap(logo_pixmap.scaled(100, 100, Qt.KeepAspectRatio)) # Resize logo
            logo_layout = QHBoxLayout()
            logo_layout.addStretch(1)  # Push logo to the left
            logo_layout.addWidget(self.logo_label)
            main_layout.addLayout(logo_layout)

        self.setLayout(main_layout)

    def load_employees(self):
        self.employee_table.setRowCount(0)
        employees = self.db_manager.get_employees()
        for employee in employees:
            row = self.employee_table.rowCount()
            self.employee_table.insertRow(row)
            for i, data in enumerate(employee):
                self.employee_table.setItem(row, i, QTableWidgetItem(str(data)))

    def filter_employees(self, text):
        text = text.lower()
        for row in range(self.employee_table.rowCount()):
            match = False
            for col in range(self.employee_table.columnCount()):
                item = self.employee_table.item(row, col)
                if item and text in item.text().lower():
                    match = True
                    break
            self.employee_table.setRowHidden(row, not match)

    def show_employee_details(self, index):
        row = index.row()
        employee_id = int(self.employee_table.item(row, 0).text())
        employee = self.db_manager.get_employee_by_id(employee_id)
        if employee:
            details_dialog = EmployeeDetailsDialog(employee, self.db_manager, self.is_dark_mode(), self.current_user, self)
            details_dialog.exec_()

    def show_add_employee_dialog(self):
        add_dialog = AddEmployeeDialog(self.db_manager, self.is_dark_mode(), self)
        if add_dialog.exec_() == QDialog.Accepted:
            self.load_employees()

    def show_edit_employee_dialog(self):
        selected_items = self.employee_table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            employee_id = int(self.employee_table.item(row, 0).text())
            employee = self.db_manager.get_employee_by_id(employee_id)
            if employee:
                edit_dialog = EditEmployeeDialog(employee, self.db_manager, self.is_dark_mode(), self)
                if edit_dialog.exec_() == QDialog.Accepted:
                    self.load_employees()
        else:
            QMessageBox.warning(self, "Warning", "No employee selected.")

    def delete_selected_employee(self):
        selected_items = self.employee_table.selectedItems()
        if selected_items:
            reply = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete the selected employee(s)?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                for item in selected_items:
                    row = item.row()
                    employee_id = int(self.employee_table.item(row, 0).text())
                    self.db_manager.delete_employee(employee_id)
                self.load_employees()
        else:
            QMessageBox.warning(self, "Warning", "No employee selected.")

    def show_add_note_dialog(self):
        selected_items = self.employee_table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            employee_id = int(self.employee_table.item(row, 0).text())
            add_note_dialog = AddNoteDialog(employee_id, self.db_manager, self.is_dark_mode(), self.current_user, self)
            if add_note_dialog.exec_() == QDialog.Accepted:
                self.show_employee_details(selected_items[0].index()) # Refresh details view
        else:
            QMessageBox.warning(self, "Warning", "No employee selected.")

    def show_add_kpi_dialog(self):
        selected_items = self.employee_table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            employee_id = int(self.employee_table.item(row, 0).text())
            add_kpi_dialog = AddKpiDialog(employee_id, self.db_manager, self.is_dark_mode(), self)
            if add_kpi_dialog.exec_() == QDialog.Accepted:
                self.show_employee_details(selected_items[0].index()) # Refresh details view
        else:
            QMessageBox.warning(self, "Warning", "No employee selected.")

    def show_email_dialog(self):
        selected_items = self.employee_table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            employee_id = int(self.employee_table.item(row, 0).text())
            employee = self.db_manager.get_employee_by_id(employee_id)
            if employee:
                email_dialog = EmailDialog(employee, self.db_manager, self.is_dark_mode(), self)
                email_dialog.exec_()
        else:
            QMessageBox.warning(self, "Warning", "No employee selected.")

    def show_export_dialog(self):
        export_dialog = ExportDialog(self.db_manager, self.is_dark_mode(), self)
        export_dialog.exec_()

    def show_settings_dialog(self):
        settings_dialog = SettingsDialog(self.settings, self)
        if settings_dialog.exec_() == QDialog.Accepted:
            # Theme change handling
            if self.is_dark_mode() != settings_dialog.dark_mode_changed: # Check if the theme was actually changed
                self.settings.setValue("dark_mode", settings_dialog.dark_mode_changed)
                QMessageBox.information(self, "Theme Change", "Please restart the application for the theme change to take effect.")
