import os
from PyQt5.QtGui import QPixmap

def get_logo_pixmap(dark_mode: bool):
    """Loads and returns the TeamTrackerPro logo as a QPixmap.

    The logo is expected to be in the 'teamtrackerpro/resources/icons' directory.
    The function handles both dark and light mode logo variations.

    Args:
        dark_mode: True if the application is in dark mode, False otherwise.

    Returns:
        A QPixmap of the logo, or None if the logo file is not found.
    """
    icon_dir = "teamtrackerpro/resources/icons"  # Path to your icons directory

    if dark_mode:
        logo_filename = "logo_dark.png"  # Or whatever your dark mode logo is named
    else:
        logo_filename = "logo_light.png" # Or whatever your light mode logo is named

    logo_path = os.path.join(icon_dir, logo_filename)

    if os.path.exists(logo_path):
        pixmap = QPixmap(logo_path)
        return pixmap
    else:
        logging.warning(f"Logo file not found: {logo_path}")
        return None