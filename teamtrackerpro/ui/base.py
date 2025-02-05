from PyQt5.QtWidgets import QDialog, QWidget
from teamtrackerpro.ui.themes import get_dark_dialog_stylesheet, get_light_dialog_stylesheet

class ThemedDialog(QDialog):
    def __init__(self, dark_mode: bool, parent=None):
        super().__init__(parent)
        self.dark_mode = dark_mode
        self.setStyleSheet(get_dark_dialog_stylesheet() if dark_mode else get_light_dialog_stylesheet())

class ThemedWidget(QWidget):
    def __init__(self, dark_mode: bool, parent=None):
        super().__init__(parent)
        self.dark_mode = dark_mode
        self.setStyleSheet("" if dark_mode else "") # Styles are applied in individual widgets