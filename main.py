"""
نقطه ورود برنامه
Application Entry Point
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt

from ui.main_window import MainWindow
import config


def main():
    """تابع اصلی"""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # تنظیم پالت تیره
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(config.Colors.BACKGROUND))
    palette.setColor(QPalette.WindowText, QColor(config.Colors.TEXT))
    palette.setColor(QPalette.Base, QColor(config.Colors.PANEL))
    palette.setColor(QPalette.AlternateBase, QColor(config.Colors.WIDGET))
    palette.setColor(QPalette.Text, QColor(config.Colors.TEXT))
    palette.setColor(QPalette.Button, QColor(config.Colors.PANEL))
    palette.setColor(QPalette.ButtonText, QColor(config.Colors.TEXT))
    palette.setColor(QPalette.Highlight, QColor(config.Colors.PRIMARY))
    palette.setColor(QPalette.HighlightedText, QColor(config.Colors.TEXT))
    app.setPalette(palette)

    # اجرای برنامه
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
