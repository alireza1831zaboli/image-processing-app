"""
استایلهای رابط کاربری - فشرده و تمیز
Compact and Clean UI Styles
"""

import config


def get_main_stylesheet() -> str:
    """استایل فشرده و مدرن"""
    return f"""
    /* ========== پنجره اصلی ========== */
    QMainWindow {{
        background-color: {config.Colors.BACKGROUND};
    }}
    
    QWidget {{
        background-color: {config.Colors.PANEL};
        color: {config.Colors.TEXT};
        font-family: {config.Fonts.FAMILY};
        font-size: {config.Fonts.SIZE_BASE}px;
    }}
    
    /* ========== دکمه‌های فشرده ========== */
    QPushButton {{
        background-color: {config.Colors.PRIMARY};
        color: white;
        border: none;
        padding: 8px 14px;
        border-radius: {config.Layout.RADIUS_MEDIUM}px;
        font-weight: 500;
        font-size: {config.Fonts.SIZE_BUTTON}px;
        min-height: {config.Layout.BUTTON_HEIGHT}px;
    }}
    
    QPushButton:hover {{
        background-color: {config.Colors.PRIMARY_HOVER};
    }}
    
    QPushButton:pressed {{
        background-color: {config.Colors.PRIMARY_DARK};
    }}
    
    QPushButton:disabled {{
        background-color: {config.Colors.WIDGET};
        color: {config.Colors.TEXT_MUTED};
    }}

        QPushButton[variant="danger"] {{
        background-color: rgba(220, 80, 80, 0.85);
        color: white;
        border: none;
    }}
    QPushButton[variant="danger"]:hover {{
        background-color: rgba(220, 80, 80, 0.95);
    }}
    QPushButton[variant="danger"]:pressed {{
        background-color: rgba(200, 70, 70, 1.0);
    }}
    
    /* ========== ComboBox ========== */
    QComboBox {{
        background-color: {config.Colors.WIDGET};
        border: 1px solid {config.Colors.BORDER};
        border-radius: {config.Layout.RADIUS_MEDIUM}px;
        padding: 6px 10px;
        min-height: {config.Layout.CONTROL_HEIGHT}px;
        color: {config.Colors.TEXT};
    }}
    
    QComboBox:hover {{
        border-color: {config.Colors.PRIMARY};
    }}
    
    QComboBox::drop-down {{
        border: none;
        width: 28px;
    }}
    
    QComboBox::down-arrow {{
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 5px solid {config.Colors.TEXT_SECONDARY};
        margin-right: 6px;
    }}
    
    QComboBox QAbstractItemView {{
        background-color: {config.Colors.PANEL};
        border: 1px solid {config.Colors.BORDER};
        border-radius: {config.Layout.RADIUS_MEDIUM}px;
        selection-background-color: {config.Colors.PRIMARY};
        padding: 3px;
        outline: none;
    }}
    
    QComboBox QAbstractItemView::item {{
        padding: 6px 10px;
        border-radius: 4px;
        min-height: 28px;
    }}
    
    QComboBox QAbstractItemView::item:hover {{
        background-color: {config.Colors.HOVER};
    }}
    
    /* ========== SpinBox ========== */
    QSpinBox, QDoubleSpinBox {{
        background-color: {config.Colors.WIDGET};
        border: 1px solid {config.Colors.BORDER};
        border-radius: {config.Layout.RADIUS_MEDIUM}px;
        padding: 6px 10px;
        min-height: {config.Layout.CONTROL_HEIGHT}px;
        color: {config.Colors.TEXT};
    }}
    
    QSpinBox:hover, QDoubleSpinBox:hover {{
        border-color: {config.Colors.PRIMARY};
    }}
    
    /* ========== Slider ========== */
    QSlider::groove:horizontal {{
        background: {config.Colors.WIDGET};
        height: 5px;
        border-radius: 2px;
        border: 1px solid {config.Colors.BORDER};
    }}
    
    QSlider::handle:horizontal {{
        background: {config.Colors.PRIMARY};
        width: 16px;
        height: 16px;
        margin: -6px 0;
        border-radius: 8px;
    }}
    
    QSlider::handle:horizontal:hover {{
        background: {config.Colors.PRIMARY_LIGHT};
        width: 18px;
        height: 18px;
        margin: -7px 0;
    }}
    
    QSlider::sub-page:horizontal {{
        background: {config.Colors.PRIMARY};
        border-radius: 2px;
    }}
    
    /* ========== GroupBox فشرده ========== */
    QGroupBox {{
        background-color: {config.Colors.PANEL};
        border: 1px solid {config.Colors.BORDER};
        border-radius: {config.Layout.RADIUS_MEDIUM}px;
        margin-top: 14px;
        padding: 14px 10px 10px 10px;
        font-weight: 500;
        color: {config.Colors.TEXT};
    }}
    
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        left: 12px;
        top: 6px;
        padding: 2px 8px;
        background-color: {config.Colors.PANEL};
        color: {config.Colors.TEXT};
        border-radius: 4px;
        font-size: {config.Fonts.SIZE_SMALL}px;
    }}
    
    /* ========== TabWidget ========== */
    QTabWidget::pane {{
        border: 1px solid {config.Colors.BORDER};
        border-radius: {config.Layout.RADIUS_MEDIUM}px;
        background-color: {config.Colors.PANEL};
        padding: 0px;
    }}
    
    QTabBar::tab {{
        background-color: transparent;
        color: {config.Colors.TEXT_SECONDARY};
        padding: 8px 20px;
        margin: 3px 3px;
        border-radius: {config.Layout.RADIUS_MEDIUM}px;
        font-weight: 500;
        font-size: {config.Fonts.SIZE_BASE}px;
        min-width: 100px;
    }}
    
    QTabBar::tab:hover {{
        background-color: {config.Colors.HOVER};
        color: {config.Colors.TEXT};
    }}
    
    QTabBar::tab:selected {{
        background-color: {config.Colors.PRIMARY};
        color: white;
    }}
    
    /* ========== ScrollBar ========== */
    QScrollBar:vertical {{
        background-color: {config.Colors.PANEL};
        width: 10px;
        border-radius: 5px;
    }}
    
    QScrollBar::handle:vertical {{
        background-color: {config.Colors.WIDGET};
        border-radius: 5px;
        min-height: 25px;
        margin: 2px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background-color: {config.Colors.PRIMARY};
    }}
    
    QScrollBar:horizontal {{
        background-color: {config.Colors.PANEL};
        height: 10px;
        border-radius: 5px;
    }}
    
    QScrollBar::handle:horizontal {{
        background-color: {config.Colors.WIDGET};
        border-radius: 5px;
        min-width: 25px;
        margin: 2px;
    }}
    
    QScrollBar::handle:horizontal:hover {{
        background-color: {config.Colors.PRIMARY};
    }}
    
    QScrollBar::add-line, QScrollBar::sub-line {{
        height: 0px;
        width: 0px;
    }}
    
    /* ========== Label ========== */
    QLabel {{
        color: {config.Colors.TEXT};
        background: transparent;
    }}
    
    /* ========== StatusBar ========== */
    QStatusBar {{
        background-color: {config.Colors.PANEL};
        border-top: 1px solid {config.Colors.BORDER};
        color: {config.Colors.TEXT_SECONDARY};
        padding: 3px 10px;
        font-size: {config.Fonts.SIZE_SMALL}px;
    }}
    """


from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QApplication


def build_qt_palette() -> QPalette:
    """ساخت QPalette مطابق رنگ‌های فعال config.Colors"""
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
    return palette


def apply_app_theme(theme: str) -> None:
    """اعمال تم در سطح کل برنامه (رنگ‌ها + پالت + استایل‌شیت)"""
    # 1) update config colors
    config.set_theme(theme)

    # 2) apply palette + stylesheet globally
    app = QApplication.instance()
    if app is None:
        return

    app.setPalette(build_qt_palette())
    app.setStyleSheet(get_main_stylesheet())
