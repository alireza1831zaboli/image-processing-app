"""
پنجره تنظیمات (اجرای لحظه‌ای + تم روشن/تیره)
Settings Dialog (Live Apply + Light/Dark Theme)
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QFormLayout,
    QLabel,
    QComboBox,
    QCheckBox,
    QPushButton,
    QWidget,
    QFrame,
    QMessageBox,
)

import config
from settings_manager import get_settings
from translations import Translations


class SettingsDialog(QDialog):
    """
    تنظیمات به‌صورت لحظه‌ای اعمال می‌شوند و همان لحظه ذخیره می‌گردند.
    """

    settings_changed = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.settings = get_settings()
        self.current_lang = self.settings.get("language", "fa")

        self.setWindowTitle(Translations.get("settings_title", self.current_lang))
        self.setMinimumSize(620, 460)
        self.setModal(True)

        self._building = False
        self._controls = {}
        self._last_theme = self.settings.get("theme", "dark")

        self.setup_ui()
        self.load_current_settings()
        self.apply_styles()
        self.apply_direction()

    # ---------- UI ----------

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header = QLabel("⚙️ " + Translations.get("settings_title", self.current_lang))
        header.setObjectName("SettingsHeader")
        layout.addWidget(header)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setObjectName("SettingsDivider")
        layout.addWidget(line)

        # --- Appearance ---
        appearance_group = QGroupBox(
            "🎨 " + Translations.get("settings_appearance", self.current_lang)
        )
        ap_form = QFormLayout()
        ap_form.setLabelAlignment(Qt.AlignLeft)
        ap_form.setFormAlignment(Qt.AlignTop)
        ap_form.setHorizontalSpacing(14)
        ap_form.setVerticalSpacing(10)

        self.language_combo = QComboBox()
        self.language_combo.addItem("🇮🇷 " + Translations.get("lang_persian", self.current_lang), "fa")
        self.language_combo.addItem("🇬🇧 " + Translations.get("lang_english", self.current_lang), "en")
        ap_form.addRow(Translations.get("settings_language", self.current_lang) + ":", self.language_combo)

        self.theme_combo = QComboBox()
        self.theme_combo.addItem("🌙 " + Translations.get("theme_dark", self.current_lang), "dark")
        self.theme_combo.addItem("☀️ " + Translations.get("theme_light", self.current_lang), "light")
        ap_form.addRow(Translations.get("settings_theme", self.current_lang) + ":", self.theme_combo)

        appearance_group.setLayout(ap_form)
        layout.addWidget(appearance_group)

        # --- UX / Interaction ---
        ux_group = QGroupBox("🧩 " + Translations.get("settings_interaction", self.current_lang))
        ux_form = QFormLayout()
        ux_form.setHorizontalSpacing(14)
        ux_form.setVerticalSpacing(10)

        self.zoom_speed_combo = QComboBox()
        self.zoom_speed_combo.addItem("🐢 " + Translations.get("speed_slow", self.current_lang), "slow")
        self.zoom_speed_combo.addItem("⚡ " + Translations.get("speed_normal", self.current_lang), "normal")
        self.zoom_speed_combo.addItem("🚀 " + Translations.get("speed_fast", self.current_lang), "fast")
        ux_form.addRow(Translations.get("zoom_speed", self.current_lang) + ":", self.zoom_speed_combo)

        self.show_hints_check = QCheckBox(Translations.get("show_hints", self.current_lang))
        ux_form.addRow(self.show_hints_check)

        self.confirm_exit_check = QCheckBox(Translations.get("confirm_exit", self.current_lang))
        ux_form.addRow(self.confirm_exit_check)

        ux_group.setLayout(ux_form)
        layout.addWidget(ux_group)

        # --- Files ---
        files_group = QGroupBox("💾 " + Translations.get("settings_files", self.current_lang))
        files_form = QFormLayout()
        files_form.setHorizontalSpacing(14)
        files_form.setVerticalSpacing(10)

        self.quality_combo = QComboBox()
        self.quality_combo.addItem(Translations.get("quality_low", self.current_lang) + " (50%)", "low")
        self.quality_combo.addItem(Translations.get("quality_medium", self.current_lang) + " (75%)", "medium")
        self.quality_combo.addItem(Translations.get("quality_high", self.current_lang) + " (90%)", "high")
        self.quality_combo.addItem(Translations.get("quality_maximum", self.current_lang) + " (100%)", "maximum")
        files_form.addRow(Translations.get("save_quality", self.current_lang) + ":", self.quality_combo)

        self.format_combo = QComboBox()
        self.format_combo.addItem("PNG", "PNG")
        self.format_combo.addItem("JPEG", "JPEG")
        self.format_combo.addItem("BMP", "BMP")
        files_form.addRow(Translations.get("default_format", self.current_lang) + ":", self.format_combo)

        files_group.setLayout(files_form)
        layout.addWidget(files_group)

        layout.addStretch(1)

        # Buttons
        btns = QHBoxLayout()
        btns.addStretch(1)

        self.reset_btn = QPushButton("🔄 " + Translations.get("btn_reset", self.current_lang))
        self.reset_btn.clicked.connect(self.reset_settings)
        btns.addWidget(self.reset_btn)

        self.close_btn = QPushButton("✅ " + Translations.get("btn_close", self.current_lang))
        self.close_btn.clicked.connect(self.accept)
        self.close_btn.setDefault(True)
        btns.addWidget(self.close_btn)

        layout.addLayout(btns)

        # Live connections
        self.language_combo.currentIndexChanged.connect(self._on_any_change)
        self.theme_combo.currentIndexChanged.connect(self._on_any_change)
        self.zoom_speed_combo.currentIndexChanged.connect(self._on_any_change)
        self.show_hints_check.toggled.connect(self._on_any_change)
        self.confirm_exit_check.toggled.connect(self._on_any_change)
        self.quality_combo.currentIndexChanged.connect(self._on_any_change)
        self.format_combo.currentIndexChanged.connect(self._on_any_change)

    def apply_direction(self):
        self.setLayoutDirection(Qt.RightToLeft if self.settings.is_rtl() else Qt.LeftToRight)

    # ---------- Data ----------

    def load_current_settings(self):
        self._building = True
        try:
            lang = self.settings.get("language", "fa")
            idx = self.language_combo.findData(lang)
            if idx >= 0:
                self.language_combo.setCurrentIndex(idx)

            theme = self.settings.get("theme", "dark")
            idx = self.theme_combo.findData(theme)
            if idx >= 0:
                self.theme_combo.setCurrentIndex(idx)

            zoom_speed = self.settings.get("zoom_speed", "normal")
            idx = self.zoom_speed_combo.findData(zoom_speed)
            if idx >= 0:
                self.zoom_speed_combo.setCurrentIndex(idx)

            self.show_hints_check.setChecked(self.settings.get("show_hints", True))
            self.confirm_exit_check.setChecked(self.settings.get("confirm_exit", True))

            quality = self.settings.get("save_quality", "high")
            idx = self.quality_combo.findData(quality)
            if idx >= 0:
                self.quality_combo.setCurrentIndex(idx)

            fmt = self.settings.get("default_format", "PNG")
            idx = self.format_combo.findData(fmt)
            if idx >= 0:
                self.format_combo.setCurrentIndex(idx)
        finally:
            self._building = False

    def _collect_settings(self) -> dict:
        return {
            "language": self.language_combo.currentData(),
            "theme": self.theme_combo.currentData(),
            "zoom_speed": self.zoom_speed_combo.currentData(),
            "show_hints": self.show_hints_check.isChecked(),
            "confirm_exit": self.confirm_exit_check.isChecked(),
            "save_quality": self.quality_combo.currentData(),
            "default_format": self.format_combo.currentData(),
        }

    def _on_any_change(self):
        if self._building:
            return

        new_settings = self._collect_settings()
        theme_changed = new_settings.get("theme") != self._last_theme

        # ذخیره و انتشار تغییرات
        self.settings.update(new_settings)
        self.settings.save()

        # اگر زبان عوض شد، UI همین دیالوگ هم باید همان لحظه به‌روز شود
        if new_settings.get("language") != self.current_lang:
            self.current_lang = new_settings["language"]
            self._refresh_texts()

        self.settings_changed.emit(new_settings)

        # اگر تم عوض شد، بعد از اعمال تم در MainWindow (slot مستقیم)،
        # استایل همین دیالوگ را هم دوباره اعمال می‌کنیم تا همه بخش‌ها همان لحظه عوض شوند.
        if theme_changed:
            self._last_theme = new_settings.get("theme")
            self.apply_styles()
            try:
                self.style().unpolish(self)
                self.style().polish(self)
            except Exception:
                pass
            self.update()

    def _refresh_texts(self):
        # عنوان
        self.setWindowTitle(Translations.get("settings_title", self.current_lang))

        # Headings & group titles
        # چون گروه‌ها/لیبل‌ها در setup ساخته شده‌اند، سریع فقط متن‌ها را به‌روز می‌کنیم
        # (برای سادگی، کل دیالوگ را بازسازی نمی‌کنیم)
        self.findChild(QLabel, "SettingsHeader").setText("⚙️ " + Translations.get("settings_title", self.current_lang))

        groups = self.findChildren(QGroupBox)
        # Order: appearance, ux, files
        if len(groups) >= 3:
            groups[0].setTitle("🎨 " + Translations.get("settings_appearance", self.current_lang))
            groups[1].setTitle("🧩 " + Translations.get("settings_interaction", self.current_lang))
            groups[2].setTitle("💾 " + Translations.get("settings_files", self.current_lang))

        # combos content
        # language
        self.language_combo.blockSignals(True)
        self.language_combo.clear()
        self.language_combo.addItem("🇮🇷 " + Translations.get("lang_persian", self.current_lang), "fa")
        self.language_combo.addItem("🇬🇧 " + Translations.get("lang_english", self.current_lang), "en")
        self.language_combo.setCurrentIndex(self.language_combo.findData(self.settings.get("language", "fa")))
        self.language_combo.blockSignals(False)

        # theme
        self.theme_combo.blockSignals(True)
        cur_theme = self.settings.get("theme", "dark")
        self.theme_combo.clear()
        self.theme_combo.addItem("🌙 " + Translations.get("theme_dark", self.current_lang), "dark")
        self.theme_combo.addItem("☀️ " + Translations.get("theme_light", self.current_lang), "light")
        self.theme_combo.setCurrentIndex(self.theme_combo.findData(cur_theme))
        self.theme_combo.blockSignals(False)

        # zoom speed
        self.zoom_speed_combo.blockSignals(True)
        cur_zoom = self.settings.get("zoom_speed", "normal")
        self.zoom_speed_combo.clear()
        self.zoom_speed_combo.addItem("🐢 " + Translations.get("speed_slow", self.current_lang), "slow")
        self.zoom_speed_combo.addItem("⚡ " + Translations.get("speed_normal", self.current_lang), "normal")
        self.zoom_speed_combo.addItem("🚀 " + Translations.get("speed_fast", self.current_lang), "fast")
        self.zoom_speed_combo.setCurrentIndex(self.zoom_speed_combo.findData(cur_zoom))
        self.zoom_speed_combo.blockSignals(False)

        # checkboxes
        self.show_hints_check.setText(Translations.get("show_hints", self.current_lang))
        self.confirm_exit_check.setText(Translations.get("confirm_exit", self.current_lang))

        # quality
        self.quality_combo.blockSignals(True)
        cur_q = self.settings.get("save_quality", "high")
        self.quality_combo.clear()
        self.quality_combo.addItem(Translations.get("quality_low", self.current_lang) + " (50%)", "low")
        self.quality_combo.addItem(Translations.get("quality_medium", self.current_lang) + " (75%)", "medium")
        self.quality_combo.addItem(Translations.get("quality_high", self.current_lang) + " (90%)", "high")
        self.quality_combo.addItem(Translations.get("quality_maximum", self.current_lang) + " (100%)", "maximum")
        self.quality_combo.setCurrentIndex(self.quality_combo.findData(cur_q))
        self.quality_combo.blockSignals(False)

        # format labels remain same, but row labels are in form layout, so easiest: rebuild dialog labels via close/reopen.
        # to keep it simple, we set layout direction and re-apply stylesheet here.
        self.apply_direction()
        self.apply_styles()

        # buttons
        self.reset_btn.setText("🔄 " + Translations.get("btn_reset", self.current_lang))
        self.close_btn.setText("✅ " + Translations.get("btn_close", self.current_lang))

    def reset_settings(self):
        reply = QMessageBox.question(
            self,
            Translations.get("btn_reset", self.current_lang),
            Translations.get("msg_reset_confirm", self.current_lang),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        self.settings.reset()
        self.settings.save()
        self.load_current_settings()
        # اعمال و انتشار
        new_settings = self._collect_settings()
        self.settings_changed.emit(new_settings)

    # ---------- Style ----------

    def apply_styles(self):
        # از رنگ‌های فعال config استفاده می‌کنیم (در لحظه با theme عوض می‌شوند)
        self.setStyleSheet(
            f"""
            QDialog {{
                background-color: {config.Colors.BACKGROUND};
                color: {config.Colors.TEXT};
            }}

            QLabel#SettingsHeader {{
                font-size: {config.Fonts.SIZE_TITLE}px;
                font-weight: 700;
                padding: 6px 2px;
                color: {config.Colors.TEXT};
                background: transparent;
            }}

            QFrame#SettingsDivider {{
                color: {config.Colors.BORDER};
                background: {config.Colors.BORDER};
                max-height: 1px;
            }}

            QGroupBox {{
                border: 1px solid {config.Colors.BORDER};
                border-radius: {config.Layout.RADIUS_MEDIUM}px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: 600;
            }}

            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
                top: 4px;
                padding: 2px 8px;
                border-radius: 4px;
                background-color: {config.Colors.PANEL};
                color: {config.Colors.TEXT};
            }}

            QComboBox, QCheckBox {{
                font-size: {config.Fonts.SIZE_BASE}px;
            }}

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

            QCheckBox {{
                color: {config.Colors.TEXT};
                spacing: 10px;
                padding: 2px 0;
            }}

            QPushButton {{
                background-color: {config.Colors.PRIMARY};
                color: white;
                border: none;
                padding: 8px 14px;
                border-radius: {config.Layout.RADIUS_MEDIUM}px;
                font-weight: 600;
                min-width: 130px;
                min-height: {config.Layout.BUTTON_HEIGHT}px;
            }}
            QPushButton:hover {{
                background-color: {config.Colors.PRIMARY_LIGHT};
            }}
            QPushButton:pressed {{
                background-color: {config.Colors.PRIMARY_DARK};
            }}
            """
        )
