import sys
import logging
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QSettings
import qdarkstyle

from teamtrackerpro.models.database_manager import DatabaseManager
from teamtrackerpro.ui.dialogs import LoginDialog
from teamtrackerpro.ui.main_window import EmployeeManagerUI

def main() -> None:
    logging.basicConfig(
        filename='teamtrackerpro.log',
        level=logging.INFO,  # Set to INFO for production
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logging.info("TeamTrackerPro application started.")

    app = QApplication(sys.argv)
    settings = QSettings("MyCompany", "TeamTrackerPro")
    dark_mode = settings.value("dark_mode", False, type=bool)

    if dark_mode:
        app.setStyleSheet(qdarkstyle.load_stylesheet())
    # Light theme is not applied by default anymore. It's up to the user.

    db_manager = DatabaseManager()
    login_dialog = LoginDialog(db_manager, dark_mode)

    if login_dialog.exec_() != LoginDialog.Accepted or not login_dialog.user:
        logging.info("Login cancelled or failed.")
        sys.exit(0)

    main_window = EmployeeManagerUI(login_dialog.user)
    main_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()