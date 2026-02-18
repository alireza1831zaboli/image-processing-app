"""
نقطه ورود برنامه
Application Entry Point
"""

import sys
from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow
from ui.styles import apply_app_theme
from settings_manager import get_settings
from PySide6.QtGui import QIcon
from config import ICON_ICO, ICON_PNG


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    icon_path = str(ICON_ICO if ICON_ICO.exists() else ICON_PNG)
    app.setWindowIcon(QIcon(icon_path))

    # Load settings and apply theme globally (palette + stylesheet)
    settings = get_settings()
    apply_app_theme(settings.get("theme", "dark"))

    window = MainWindow()
    window.setWindowIcon(app.windowIcon())
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
