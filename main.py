"""
نقطه ورود برنامه
Application Entry Point
"""

import sys
from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow
from ui.styles import apply_app_theme
from settings_manager import get_settings


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Load settings and apply theme globally (palette + stylesheet)
    settings = get_settings()
    apply_app_theme(settings.get("theme", "dark"))

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
