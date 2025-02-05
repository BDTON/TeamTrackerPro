from PyQt5.QtWidgets import QPushButton, QLineEdit, QTextEdit, QComboBox
from PyQt5.QtCore import QSize, Qt

class AnimatedButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: #5865F2; /* Primary color */
                color: white;
                border-radius: 5px;
                padding: 8px 16px;
                transition: background-color 0.3s ease; /* Smooth transition */
            }
            QPushButton:hover {
                background-color: #4441E4; /* Darker shade on hover */
            }
            QPushButton:pressed {
                background-color: #3330D3; /* Even darker on click */
            }
        """)

class StyledLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QLineEdit {
                background-color: #F4F4F4; /* Light gray */
                border: 1px solid #CCCCCC; /* Light gray border */
                padding: 5px;
                border-radius: 3px;
            }
        """)

class StyledTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QTextEdit {
                background-color: #F4F4F4; /* Light gray */
                border: 1px solid #CCCCCC; /* Light gray border */
                padding: 5px;
            }
        """)

class StyledComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QComboBox {
                background-color: #F4F4F4; /* Light gray */
                border: 1px solid #CCCCCC; /* Light gray border */
                padding: 5px;
                border-radius: 3px;
            }
            QComboBox::drop-down {
                border: 0px; /* No border for the dropdown arrow */
            }
        """)