"""
استایل‌های رابط کاربری
UI Styles
"""

import config


def get_main_stylesheet() -> str:
    """استایل اصلی برنامه"""
    return f"""
        QMainWindow {{
            background-color: {config.Colors.BACKGROUND};
        }}
        
        QWidget {{
            background-color: {config.Colors.PANEL};
            color: {config.Colors.TEXT};
            font-family: {config.Fonts.FAMILY};
            font-size: {config.Fonts.SIZE_BASE}px;
        }}
        
        QPushButton {{
            background-color: {config.Colors.PRIMARY};
            color: white;
            border: none;
            padding: 10px;
            border-radius: 5px;
            font-weight: bold;
            min-height: 35px;
        }}
        
        QPushButton:hover {{
            background-color: {config.Colors.PRIMARY_LIGHT};
        }}
        
        QPushButton:pressed {{
            background-color: {config.Colors.PRIMARY_DARK};
        }}
        
        QPushButton:disabled {{
            background-color: #555555;
            color: #888888;
        }}
        
        QComboBox, QSpinBox, QDoubleSpinBox {{
            background-color: {config.Colors.WIDGET};
            border: 2px solid #555555;
            border-radius: 5px;
            padding: 5px;
            min-height: 30px;
        }}
        
        QComboBox:hover, QSpinBox:hover, QDoubleSpinBox:hover {{
            border-color: {config.Colors.PRIMARY};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 30px;
        }}
        
        QSlider::groove:horizontal {{
            background: {config.Colors.WIDGET};
            height: 8px;
            border-radius: 4px;
        }}
        
        QSlider::handle:horizontal {{
            background: {config.Colors.PRIMARY};
            width: 18px;
            margin: -5px 0;
            border-radius: 9px;
        }}
        
        QSlider::handle:horizontal:hover {{
            background: {config.Colors.PRIMARY_LIGHT};
        }}
        
        QGroupBox {{
            border: 2px solid {config.Colors.BORDER};
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 15px;
            font-weight: bold;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }}
        
        QTabWidget::pane {{
            border: 2px solid {config.Colors.BORDER};
            border-radius: 5px;
            background-color: {config.Colors.PANEL};
        }}
        
        QTabBar::tab {{
            background-color: {config.Colors.WIDGET};
            color: {config.Colors.TEXT};
            padding: 10px 15px;
            margin-right: 2px;
            border-top-left-radius: 5px;
            border-top-right-radius: 5px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {config.Colors.PRIMARY};
        }}
        
        QTabBar::tab:hover {{
            background-color: #4d4d4d;
        }}
        
        QLabel {{
            color: {config.Colors.TEXT};
        }}
        
        QScrollBar:vertical {{
            background-color: {config.Colors.PANEL};
            width: 12px;
            margin: 0px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {config.Colors.PRIMARY};
            border-radius: 6px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {config.Colors.PRIMARY_LIGHT};
        }}
        
        QScrollBar:horizontal {{
            background-color: {config.Colors.PANEL};
            height: 12px;
            margin: 0px;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: {config.Colors.PRIMARY};
            border-radius: 6px;
            min-width: 20px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background-color: {config.Colors.PRIMARY_LIGHT};
        }}
    """
