"""
پنجره تنظیمات کامل - اصلاح شده
Complete Settings Dialog - Fixed
"""

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QWidget,
    QLabel,
    QComboBox,
    QCheckBox,
    QSpinBox,
    QPushButton,
    QGroupBox,
    QFormLayout,
    QMessageBox,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import config
from translations import Translations
from settings_manager import get_settings


class SettingsDialog(QDialog):
    """پنجره تنظیمات"""

    settings_applied = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = get_settings()
        self.current_lang = self.settings.get("language", "fa")

        self.setWindowTitle(Translations.get("settings_title", self.current_lang))
        self.setMinimumSize(600, 500)
        self.setModal(True)

        self.setup_ui()
        self.load_current_settings()
        self.apply_styles()

    def setup_ui(self):
        """ساخت UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        # تب‌ها
        self.tabs = QTabWidget()

        # تب 1: ظاهری
        self.appearance_tab = self.create_appearance_tab()
        self.tabs.addTab(
            self.appearance_tab,
            "🎨 " + Translations.get("settings_appearance", self.current_lang),
        )

        # تب 2: عملکرد
        self.performance_tab = self.create_performance_tab()
        self.tabs.addTab(
            self.performance_tab,
            "⚙️ " + Translations.get("settings_performance", self.current_lang),
        )

        # تب 3: فایل‌ها
        self.files_tab = self.create_files_tab()
        self.tabs.addTab(
            self.files_tab,
            "💾 " + Translations.get("settings_files", self.current_lang),
        )

        # تب 4: پیشرفته
        self.advanced_tab = self.create_advanced_tab()
        self.tabs.addTab(
            self.advanced_tab,
            "🔧 " + Translations.get("settings_advanced", self.current_lang),
        )

        layout.addWidget(self.tabs)

        # دکمه‌ها
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        self.reset_btn = QPushButton(
            "🔄 " + Translations.get("btn_reset", self.current_lang)
        )
        self.reset_btn.clicked.connect(self.reset_settings)
        buttons_layout.addWidget(self.reset_btn)

        self.cancel_btn = QPushButton(
            "❌ " + Translations.get("btn_cancel", self.current_lang)
        )
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_btn)

        self.apply_btn = QPushButton(
            "✅ " + Translations.get("btn_apply", self.current_lang)
        )
        self.apply_btn.clicked.connect(self.apply_settings)
        self.apply_btn.setDefault(True)
        buttons_layout.addWidget(self.apply_btn)

        layout.addLayout(buttons_layout)

    def create_appearance_tab(self):
        """تب ظاهری"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)

        # گروه زبان
        lang_group = QGroupBox(
            "🌐 " + Translations.get("settings_language", self.current_lang)
        )
        lang_layout = QFormLayout()

        self.language_combo = QComboBox()
        self.language_combo.addItem(
            "🇮🇷 " + Translations.get("lang_persian", self.current_lang), "fa"
        )
        self.language_combo.addItem(
            "🇬🇧 " + Translations.get("lang_english", self.current_lang), "en"
        )
        lang_layout.addRow(
            Translations.get("settings_language", self.current_lang) + ":",
            self.language_combo,
        )

        lang_group.setLayout(lang_layout)
        layout.addWidget(lang_group)

        # گروه پوسته
        theme_group = QGroupBox(
            "🎨 " + Translations.get("settings_theme", self.current_lang)
        )
        theme_layout = QFormLayout()

        self.theme_combo = QComboBox()
        self.theme_combo.addItem(
            "🌙 " + Translations.get("theme_dark", self.current_lang), "dark"
        )
        self.theme_combo.addItem(
            "☀️ " + Translations.get("theme_light", self.current_lang), "light"
        )
        self.theme_combo.addItem(
            "🤖 " + Translations.get("theme_auto", self.current_lang), "auto"
        )
        theme_layout.addRow(
            Translations.get("settings_theme", self.current_lang) + ":",
            self.theme_combo,
        )

        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)

        # گروه Grid
        grid_group = QGroupBox("📐 Grid")
        grid_layout = QFormLayout()

        self.show_grid_check = QCheckBox(
            Translations.get("show_grid", self.current_lang)
        )
        grid_layout.addRow(self.show_grid_check)

        self.grid_size_spin = QSpinBox()
        self.grid_size_spin.setRange(8, 64)
        self.grid_size_spin.setSingleStep(8)
        self.grid_size_spin.setSuffix(
            " " + Translations.get("unit_pixels", self.current_lang)
        )
        grid_layout.addRow(
            Translations.get("grid_size", self.current_lang) + ":", self.grid_size_spin
        )

        grid_group.setLayout(grid_layout)
        layout.addWidget(grid_group)

        layout.addStretch()
        return widget

    def create_performance_tab(self):
        """تب عملکرد"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)

        # گروه سرعت Zoom
        zoom_group = QGroupBox(
            "🔍 " + Translations.get("zoom_speed", self.current_lang)
        )
        zoom_layout = QFormLayout()

        self.zoom_speed_combo = QComboBox()
        self.zoom_speed_combo.addItem(
            "🐢 " + Translations.get("speed_slow", self.current_lang), "slow"
        )
        self.zoom_speed_combo.addItem(
            "⚡ " + Translations.get("speed_normal", self.current_lang), "normal"
        )
        self.zoom_speed_combo.addItem(
            "🚀 " + Translations.get("speed_fast", self.current_lang), "fast"
        )
        zoom_layout.addRow(
            Translations.get("zoom_speed", self.current_lang) + ":",
            self.zoom_speed_combo,
        )

        zoom_group.setLayout(zoom_layout)
        layout.addWidget(zoom_group)

        # گروه History
        history_group = QGroupBox(
            "📜 " + Translations.get("history_size", self.current_lang)
        )
        history_layout = QFormLayout()

        self.history_size_spin = QSpinBox()
        self.history_size_spin.setRange(5, 50)
        self.history_size_spin.setSingleStep(5)
        self.history_size_spin.setSuffix(
            " " + Translations.get("unit_steps", self.current_lang)
        )
        history_layout.addRow(
            Translations.get("history_size", self.current_lang) + ":",
            self.history_size_spin,
        )

        history_group.setLayout(history_layout)
        layout.addWidget(history_group)

        # گروه Auto-save
        autosave_group = QGroupBox(
            "💾 " + Translations.get("auto_save", self.current_lang)
        )
        autosave_layout = QFormLayout()

        self.auto_save_check = QCheckBox(
            Translations.get("auto_save", self.current_lang)
        )
        autosave_layout.addRow(self.auto_save_check)

        self.auto_save_interval_spin = QSpinBox()
        self.auto_save_interval_spin.setRange(1, 60)
        self.auto_save_interval_spin.setSingleStep(5)
        self.auto_save_interval_spin.setSuffix(
            " " + Translations.get("unit_minutes", self.current_lang)
        )
        autosave_layout.addRow(
            Translations.get("auto_save_interval", self.current_lang) + ":",
            self.auto_save_interval_spin,
        )

        autosave_group.setLayout(autosave_layout)
        layout.addWidget(autosave_group)

        layout.addStretch()
        return widget

    def create_files_tab(self):
        """تب فایل‌ها"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)

        # گروه کیفیت
        quality_group = QGroupBox(
            "🎯 " + Translations.get("save_quality", self.current_lang)
        )
        quality_layout = QFormLayout()

        self.quality_combo = QComboBox()
        self.quality_combo.addItem(
            Translations.get("quality_low", self.current_lang) + " (50%)", "low"
        )
        self.quality_combo.addItem(
            Translations.get("quality_medium", self.current_lang) + " (75%)", "medium"
        )
        self.quality_combo.addItem(
            Translations.get("quality_high", self.current_lang) + " (90%)", "high"
        )
        self.quality_combo.addItem(
            Translations.get("quality_maximum", self.current_lang) + " (100%)",
            "maximum",
        )
        quality_layout.addRow(
            Translations.get("save_quality", self.current_lang) + ":",
            self.quality_combo,
        )

        quality_group.setLayout(quality_layout)
        layout.addWidget(quality_group)

        # گروه فرمت
        format_group = QGroupBox(
            "📄 " + Translations.get("default_format", self.current_lang)
        )
        format_layout = QFormLayout()

        self.format_combo = QComboBox()
        self.format_combo.addItem("PNG", "PNG")
        self.format_combo.addItem("JPEG", "JPEG")
        self.format_combo.addItem("BMP", "BMP")
        format_layout.addRow(
            Translations.get("default_format", self.current_lang) + ":",
            self.format_combo,
        )

        format_group.setLayout(format_layout)
        layout.addWidget(format_group)

        layout.addStretch()
        return widget

    def create_advanced_tab(self):
        """تب پیشرفته"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)

        # گروه رابط کاربری
        ui_group = QGroupBox("🖥️ Interface")
        ui_layout = QFormLayout()

        self.show_hints_check = QCheckBox(
            Translations.get("show_hints", self.current_lang)
        )
        ui_layout.addRow(self.show_hints_check)

        self.confirm_exit_check = QCheckBox(
            Translations.get("confirm_exit", self.current_lang)
        )
        ui_layout.addRow(self.confirm_exit_check)

        ui_group.setLayout(ui_layout)
        layout.addWidget(ui_group)

        # گروه Canvas
        canvas_group = QGroupBox("📐 Canvas")
        canvas_layout = QFormLayout()

        self.canvas_size_combo = QComboBox()
        self.canvas_size_combo.addItem("Small (800×400)", "small")
        self.canvas_size_combo.addItem("Normal (1000×500)", "normal")
        self.canvas_size_combo.addItem("Large (1200×600)", "large")
        canvas_layout.addRow("Canvas Size:", self.canvas_size_combo)

        self.antialiasing_check = QCheckBox("Antialiasing")
        canvas_layout.addRow(self.antialiasing_check)

        canvas_group.setLayout(canvas_layout)
        layout.addWidget(canvas_group)

        layout.addStretch()
        return widget

    def load_current_settings(self):
        """بارگذاری تنظیمات فعلی"""
        # ظاهری
        lang = self.settings.get("language", "fa")
        index = self.language_combo.findData(lang)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)

        theme = self.settings.get("theme", "dark")
        index = self.theme_combo.findData(theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)

        self.show_grid_check.setChecked(self.settings.get("show_grid", False))
        self.grid_size_spin.setValue(self.settings.get("grid_size", 16))

        # عملکرد
        zoom_speed = self.settings.get("zoom_speed", "normal")
        index = self.zoom_speed_combo.findData(zoom_speed)
        if index >= 0:
            self.zoom_speed_combo.setCurrentIndex(index)

        self.history_size_spin.setValue(self.settings.get("history_size", 10))
        self.auto_save_check.setChecked(self.settings.get("auto_save", False))
        self.auto_save_interval_spin.setValue(
            self.settings.get("auto_save_interval", 10)
        )

        # فایل‌ها
        quality = self.settings.get("save_quality", "high")
        index = self.quality_combo.findData(quality)
        if index >= 0:
            self.quality_combo.setCurrentIndex(index)

        format_val = self.settings.get("default_format", "PNG")
        index = self.format_combo.findData(format_val)
        if index >= 0:
            self.format_combo.setCurrentIndex(index)

        # پیشرفته
        self.show_hints_check.setChecked(self.settings.get("show_hints", True))
        self.confirm_exit_check.setChecked(self.settings.get("confirm_exit", True))

        canvas_size = self.settings.get("canvas_size", "normal")
        index = self.canvas_size_combo.findData(canvas_size)
        if index >= 0:
            self.canvas_size_combo.setCurrentIndex(index)

        self.antialiasing_check.setChecked(self.settings.get("antialiasing", True))

    def apply_settings(self):
        """اعمال تنظیمات"""
        new_settings = {
            "language": self.language_combo.currentData(),
            "theme": self.theme_combo.currentData(),
            "show_grid": self.show_grid_check.isChecked(),
            "grid_size": self.grid_size_spin.value(),
            "zoom_speed": self.zoom_speed_combo.currentData(),
            "history_size": self.history_size_spin.value(),
            "auto_save": self.auto_save_check.isChecked(),
            "auto_save_interval": self.auto_save_interval_spin.value(),
            "save_quality": self.quality_combo.currentData(),
            "default_format": self.format_combo.currentData(),
            "show_hints": self.show_hints_check.isChecked(),
            "confirm_exit": self.confirm_exit_check.isChecked(),
            "canvas_size": self.canvas_size_combo.currentData(),
            "antialiasing": self.antialiasing_check.isChecked(),
        }

        self.settings.update(new_settings)
        self.settings.save()
        self.settings_applied.emit(new_settings)

        QMessageBox.information(
            self,
            Translations.get("msg_success", self.current_lang),
            "Settings applied successfully!",
        )
        self.accept()

    def reset_settings(self):
        """بازنشانی تنظیمات"""
        reply = QMessageBox.question(
            self,
            Translations.get("btn_reset", self.current_lang),
            "Reset all settings to default?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.settings.reset()
            self.settings.save()
            self.load_current_settings()
            QMessageBox.information(
                self,
                Translations.get("msg_success", self.current_lang),
                "Settings reset successfully!",
            )

    def apply_styles(self):
        """استایل‌ها - اصلاح شده برای config موجود"""
        self.setStyleSheet(
            f"""
            QDialog {{
                background-color: {config.Colors.BACKGROUND};
                color: {config.Colors.TEXT};
            }}
            QTabWidget::pane {{
                border: 2px solid {config.Colors.BORDER};
                border-radius: 8px;
                background-color: {config.Colors.PANEL};
                padding: 10px;
            }}
            QTabBar::tab {{
                background-color: {config.Colors.WIDGET};
                color: {config.Colors.TEXT};
                padding: 10px 20px;
                margin: 2px;
                border: 1px solid {config.Colors.BORDER};
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }}
            QTabBar::tab:selected {{
                background-color: {config.Colors.PRIMARY};
                color: white;
                font-weight: bold;
            }}
            QGroupBox {{
                border: 2px solid {config.Colors.BORDER};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
            }}
            QPushButton {{
                background-color: {config.Colors.PRIMARY};
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 6px;
                font-weight: bold;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: {config.Colors.PRIMARY_LIGHT};
            }}
            QPushButton:pressed {{
                background-color: {config.Colors.PRIMARY_DARK};
            }}
            QPushButton:default {{
                background-color: {config.Colors.PRIMARY};
                border: 2px solid {config.Colors.PRIMARY_LIGHT};
            }}
            QComboBox, QSpinBox {{
                background-color: {config.Colors.WIDGET};
                color: {config.Colors.TEXT};
                border: 2px solid {config.Colors.BORDER};
                border-radius: 6px;
                padding: 5px;
                min-width: 200px;
            }}
            QCheckBox {{
                color: {config.Colors.TEXT};
                spacing: 8px;
            }}
        """
        )
