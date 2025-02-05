from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt

# Global color definitions
CUSTOM_PRIMARY_COLOR = "#5865F2"  # Default primary blue
CUSTOM_TEXT_COLOR_LIGHT = "#222222"  # Dark text for light mode
CUSTOM_TEXT_COLOR_DARK = "#FFFFFF"  # Light text for dark mode
CUSTOM_BACKGROUND_COLOR_LIGHT = "#FFFFFF"  # White background for light mode
CUSTOM_BACKGROUND_COLOR_DARK = "#2F3136"  # Dark background for dark mode
CUSTOM_SECONDARY_COLOR_LIGHT = "#F4F4F4"  # Light gray for secondary elements (light mode)
CUSTOM_SECONDARY_COLOR_DARK = "#40444B"  # Darker gray for secondary elements (dark mode)


def get_dark_palette():
    palette = QPalette()

    # Window background
    palette.setColor(QPalette.Window, QColor(CUSTOM_BACKGROUND_COLOR_DARK))
    palette.setColor(QPalette.WindowText, QColor(CUSTOM_TEXT_COLOR_DARK))

    # Base (used for text edits, etc.)
    palette.setColor(QPalette.Base, QColor(CUSTOM_SECONDARY_COLOR_DARK))
    palette.setColor(QPalette.Text, QColor(CUSTOM_TEXT_COLOR_DARK))

    # Button-like elements
    palette.setColor(QPalette.Button, QColor(CUSTOM_PRIMARY_COLOR))
    palette.setColor(QPalette.ButtonText, QColor(CUSTOM_TEXT_COLOR_DARK))

    # Highlighted text
    palette.setColor(QPalette.Highlight, QColor(CUSTOM_PRIMARY_COLOR))
    palette.setColor(QPalette.HighlightedText, QColor(CUSTOM_TEXT_COLOR_DARK))

    # Tooltips
    palette.setColor(QPalette.ToolTipBase, QColor(CUSTOM_BACKGROUND_COLOR_DARK))
    palette.setColor(QPalette.ToolTipText, QColor(CUSTOM_TEXT_COLOR_DARK))

    return palette

def get_light_palette():
    palette = QPalette()

    # Window background
    palette.setColor(QPalette.Window, QColor(CUSTOM_BACKGROUND_COLOR_LIGHT))
    palette.setColor(QPalette.WindowText, QColor(CUSTOM_TEXT_COLOR_LIGHT))

    # Base (used for text edits, etc.)
    palette.setColor(QPalette.Base, QColor(CUSTOM_SECONDARY_COLOR_LIGHT))
    palette.setColor(QPalette.Text, QColor(CUSTOM_TEXT_COLOR_LIGHT))

    # Button-like elements
    palette.setColor(QPalette.Button, QColor(CUSTOM_PRIMARY_COLOR))
    palette.setColor(QPalette.ButtonText, QColor(CUSTOM_TEXT_COLOR_LIGHT))

    # Highlighted text
    palette.setColor(QPalette.Highlight, QColor(CUSTOM_PRIMARY_COLOR))
    palette.setColor(QPalette.HighlightedText, QColor(CUSTOM_TEXT_COLOR_LIGHT))

    # Tooltips
    palette.setColor(QPalette.ToolTipBase, QColor(CUSTOM_BACKGROUND_COLOR_LIGHT))
    palette.setColor(QPalette.ToolTipText, QColor(CUSTOM_TEXT_COLOR_LIGHT))

    return palette

def get_dark_dialog_stylesheet():
    return f"""
        QDialog {{
            background-color: {CUSTOM_BACKGROUND_COLOR_DARK};
        }}
        QLabel {{
            color: {CUSTOM_TEXT_COLOR_DARK};
        }}
        QPushButton {{
            background-color: {CUSTOM_PRIMARY_COLOR};
            color: {CUSTOM_TEXT_COLOR_DARK};
            border-radius: 5px;
            padding: 5px 10px;
        }}
        QLineEdit {{
            background-color: {CUSTOM_SECONDARY_COLOR_DARK};
            color: {CUSTOM_TEXT_COLOR_DARK};
            border: 1px solid #666;
            padding: 3px;
        }}
        QTextEdit {{
            background-color: {CUSTOM_SECONDARY_COLOR_DARK};
            color: {CUSTOM_TEXT_COLOR_DARK};
            border: 1px solid #666;
        }}
        QComboBox {{
            background-color: {CUSTOM_SECONDARY_COLOR_DARK};
            color: {CUSTOM_TEXT_COLOR_DARK};
            border: 1px solid #666;
        }}

    """

def get_light_dialog_stylesheet():
    return f"""
        QDialog {{
            background-color: {CUSTOM_BACKGROUND_COLOR_LIGHT};
        }}
        QLabel {{
            color: {CUSTOM_TEXT_COLOR_LIGHT};
        }}
        QPushButton {{
            background-color: {CUSTOM_PRIMARY_COLOR};
            color: {CUSTOM_TEXT_COLOR_LIGHT};
            border-radius: 5px;
            padding: 5px 10px;
        }}
        QLineEdit {{
            background-color: {CUSTOM_SECONDARY_COLOR_LIGHT};
            color: {CUSTOM_TEXT_COLOR_LIGHT};
            border: 1px solid #ccc;
            padding: 3px;
        }}
        QTextEdit {{
            background-color: {CUSTOM_SECONDARY_COLOR_LIGHT};
            color: {CUSTOM_TEXT_COLOR_LIGHT};
            border: 1px solid #ccc;
        }}
        QComboBox {{
            background-color: {CUSTOM_SECONDARY_COLOR_LIGHT};
            color: {CUSTOM_TEXT_COLOR_LIGHT};
            border: 1px solid #ccc;
        }}
    """