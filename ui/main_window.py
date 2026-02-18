"""
پنجره اصلی نهایی با سیستم تنظیمات کامل
Final Main Window with Complete Settings System
"""

from PySide6.QtGui import QTextCursor

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QGroupBox,
    QFileDialog,
    QMessageBox,
    QFrame,
    QTabWidget,
    QTextEdit,
)
from PySide6.QtCore import Qt
import config
from ui.image_viewer import ImageViewer
from ui.synced_histogram_viewer import SyncedHistogramViewer
from ui.control_panel import ControlPanel
from ui.settings_dialog import SettingsDialog
from ui.styles import get_main_stylesheet, apply_app_theme
from ui.transformation_dialog import TransformationDialog
from core.image_manager import ImageManager
from core.processing_thread import ProcessingThread
from translations import Translations
from settings_manager import get_settings
import os
import numpy as np


class MainWindow(QMainWindow):
    """پنجره اصلی"""

    def __init__(self):
        super().__init__()

        # مدیریت تنظیمات
        self.settings = get_settings()
        self.current_lang = self.settings.get("language", "fa")

        # عنوان پنجره
        self.setWindowTitle(Translations.get("app_title", self.current_lang))
        # Tab titles
        if hasattr(self, "view_tabs"):
            self.view_tabs.setTabText(
                0, Translations.get("image_view", self.current_lang)
            )
            self.view_tabs.setTabText(
                1, Translations.get("histogram_view", self.current_lang)
            )

        # Viewer group titles
        if hasattr(self, "original_group"):
            self.original_group.setTitle(
                Translations.get("original_image", self.current_lang)
            )
        if hasattr(self, "processed_group"):
            self.processed_group.setTitle(
                Translations.get("processed_image", self.current_lang)
            )

        # Console title
        self.update_console_title()

        # عناوین گروه‌ها
        if hasattr(self, "original_group"):
            self.original_group.setTitle(
                Translations.get("original_image", self.current_lang)
            )
        if hasattr(self, "processed_group"):
            self.processed_group.setTitle(
                Translations.get("processed_image", self.current_lang)
            )
        if hasattr(self, "original_hist_group"):
            self.original_hist_group.setTitle(
                Translations.get("original_histogram", self.current_lang)
            )
        if hasattr(self, "processed_hist_group"):
            self.processed_hist_group.setTitle(
                Translations.get("processed_histogram", self.current_lang)
            )

        # عناوین گروه‌ها
        if hasattr(self, "original_group"):
            self.original_group.setTitle(
                Translations.get("original_image", self.current_lang)
            )
        if hasattr(self, "processed_group"):
            self.processed_group.setTitle(
                Translations.get("processed_image", self.current_lang)
            )
        if hasattr(self, "original_hist_group"):
            self.original_hist_group.setTitle(
                Translations.get("original_histogram", self.current_lang)
            )
        if hasattr(self, "processed_hist_group"):
            self.processed_hist_group.setTitle(
                Translations.get("processed_histogram", self.current_lang)
            )
        self.setGeometry(100, 100, config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        self.setMinimumSize(config.WINDOW_MIN_WIDTH, config.WINDOW_MIN_HEIGHT)

        # متغیرها
        self.original_image = None
        self.current_image = None
        self.processing_thread = None
        self._retired_threads = []  # threads we stopped but are still finishing
        self.current_filter_key = "original"
        self.current_filter_name = Translations.get(
            "filter_original", self.current_lang
        )
        self.current_filename = ""

        # Console log entries (so we can re-render them on theme change)
        # Each entry: (timestamp_str, level, message)
        self._log_entries = []

        self.syncing = False
        self.syncing_histograms = False

        self.setup_ui()
        apply_app_theme(self.settings.get("theme", "dark"))
        # self.control_panel.custom_kernel_clicked.connect(self.show_custom_kernel_dialog)

    def setup_ui(self):
        """ساخت UI"""
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Layout اصلی
        content_layout = QHBoxLayout()
        content_layout.setSpacing(config.Layout.SPACING_MEDIUM)
        content_layout.setContentsMargins(
            config.Layout.PADDING_MEDIUM,
            config.Layout.PADDING_MEDIUM,
            config.Layout.PADDING_MEDIUM,
            config.Layout.PADDING_SMALL,
        )

        # پنل کنترل
        self.control_panel = ControlPanel()
        self.control_panel.setFixedWidth(config.CONTROL_PANEL_WIDTH)
        self.control_panel.filter_changed.connect(self.apply_filter)
        self.control_panel.load_clicked.connect(self.load_image)
        self.control_panel.save_clicked.connect(self.save_image)
        self.control_panel.reset_clicked.connect(self.reset_image)
        self.control_panel.settings_clicked.connect(self.show_settings)
        self.control_panel.zoom_in_clicked.connect(self.zoom_in_viewers)
        self.control_panel.zoom_out_clicked.connect(self.zoom_out_viewers)
        self.control_panel.zoom_reset_clicked.connect(self.zoom_reset_viewers)
        self.control_panel.custom_kernel_clicked.connect(self.show_custom_kernel_dialog)
        self.control_panel.transformation_clicked.connect(
            self.show_transformation_dialog
        )

        content_layout.addWidget(self.control_panel)

        # تب‌ها
        self.view_tabs = QTabWidget()
        self.view_tabs.setTabPosition(QTabWidget.North)

        # تب تصویر
        image_tab = QWidget()
        image_layout = self.create_image_viewers()
        image_tab.setLayout(image_layout)
        self.view_tabs.addTab(
            image_tab, Translations.get("image_view", self.current_lang)
        )

        # تب هیستوگرام
        histogram_tab = QWidget()
        histogram_layout = self.create_histogram_viewers()
        histogram_tab.setLayout(histogram_layout)
        self.view_tabs.addTab(
            histogram_tab, Translations.get("histogram_view", self.current_lang)
        )

        content_layout.addWidget(self.view_tabs, stretch=1)
        main_layout.addLayout(content_layout)

        self.console_group = QGroupBox(
            Translations.get("console_title", self.current_lang)
        )
        self.console_group.setMaximumHeight(config.CONSOLE_HEIGHT)
        console_layout = QVBoxLayout()
        console_layout.setContentsMargins(
            config.Layout.PADDING_SMALL,
            config.Layout.PADDING_SMALL,
            config.Layout.PADDING_SMALL,
            config.Layout.PADDING_SMALL,
        )

        self.console_text = QTextEdit()
        self.console_text.setReadOnly(True)
        self.console_text.setMaximumHeight(config.CONSOLE_HEIGHT - 20)
        self.update_console_styles()

        # پیام خوش‌آمدگویی
        self.log("Application started successfully", "success")
        self.log("Ready to process images", "info")

        console_layout.addWidget(self.console_text)
        self.console_group.setLayout(console_layout)

        main_layout.addWidget(self.console_group)

        # نوار وضعیت
        self.create_status_bar()
        main_layout.addWidget(self.status_frame)

    def create_image_viewers(self):
        """ایجاد viewer های تصویر"""
        viewers_layout = QHBoxLayout()
        viewers_layout.setSpacing(10)

        # تصویر اصلی
        self.original_group = QGroupBox(
            Translations.get("original_image", self.current_lang)
        )
        original_layout = QVBoxLayout()
        self.original_viewer = ImageViewer()
        self.original_viewer.load_requested.connect(self.load_image)
        self.original_viewer.set_placeholder_text(
            Translations.get("msg_no_image", self.current_lang),
            Translations.get("load_image", self.current_lang),
        )
        self.original_viewer.placeholder_button.setText(
            "📂 " + Translations.get("load_image", self.current_lang)
        )
        self.original_viewer.sync_enabled = True
        self.original_viewer.mouse_moved.connect(self.on_original_mouse_moved)
        self.original_viewer.mouse_left.connect(self.on_original_mouse_left)
        self.original_viewer.zoom_changed.connect(self.on_original_zoom_changed)
        self.original_viewer.pan_changed.connect(self.on_original_pan_changed)
        original_layout.addWidget(self.original_viewer)
        self.original_group.setLayout(original_layout)
        viewers_layout.addWidget(self.original_group)

        # تصویر پردازش شده
        self.processed_group = QGroupBox(
            Translations.get("processed_image", self.current_lang)
        )
        processed_layout = QVBoxLayout()
        self.processed_viewer = ImageViewer()
        self.processed_viewer.load_requested.connect(self.load_image)
        self.processed_viewer.set_placeholder_text(
            Translations.get("msg_no_image", self.current_lang),
            Translations.get("load_image", self.current_lang),
        )
        self.processed_viewer.placeholder_button.setText(
            "📂 " + Translations.get("load_image", self.current_lang)
        )
        self.processed_viewer.sync_enabled = True
        self.processed_viewer.mouse_moved.connect(self.on_processed_mouse_moved)
        self.processed_viewer.mouse_left.connect(self.on_processed_mouse_left)
        self.processed_viewer.zoom_changed.connect(self.on_processed_zoom_changed)
        self.processed_viewer.pan_changed.connect(self.on_processed_pan_changed)
        processed_layout.addWidget(self.processed_viewer)
        self.processed_group.setLayout(processed_layout)
        viewers_layout.addWidget(self.processed_group)

        return viewers_layout

    def create_histogram_viewers(self):
        """ایجاد viewer های هیستوگرام"""
        viewers_layout = QHBoxLayout()
        viewers_layout.setSpacing(10)

        # هیستوگرام اصلی
        self.original_hist_group = QGroupBox(
            Translations.get("original_histogram", self.current_lang)
        )
        original_hist_layout = QVBoxLayout()
        self.original_histogram = SyncedHistogramViewer()
        self.original_histogram.sync_enabled = True
        self.original_histogram.zoom_changed.connect(self.on_original_hist_zoom_changed)
        self.original_histogram.pan_changed.connect(self.on_original_hist_pan_changed)
        original_hist_layout.addWidget(self.original_histogram)
        self.original_hist_group.setLayout(original_hist_layout)
        viewers_layout.addWidget(self.original_hist_group)

        # هیستوگرام پردازش شده
        self.processed_hist_group = QGroupBox(
            Translations.get("processed_histogram", self.current_lang)
        )
        processed_hist_layout = QVBoxLayout()
        self.processed_histogram = SyncedHistogramViewer()
        self.processed_histogram.sync_enabled = True
        self.processed_histogram.zoom_changed.connect(
            self.on_processed_hist_zoom_changed
        )
        self.processed_histogram.pan_changed.connect(self.on_processed_hist_pan_changed)
        processed_hist_layout.addWidget(self.processed_histogram)
        self.processed_hist_group.setLayout(processed_hist_layout)
        viewers_layout.addWidget(self.processed_hist_group)

        return viewers_layout

    # ========== همگام‌سازی تصاویر ==========

    def on_original_mouse_moved(self, x: int, y: int):
        self.update_mouse_coords(x, y)
        if x >= 0 and y >= 0:
            self.processed_viewer.set_crosshair(x, y)
        else:
            self.processed_viewer.clear_crosshair()

    def on_processed_mouse_moved(self, x: int, y: int):
        self.update_mouse_coords(x, y)
        if x >= 0 and y >= 0:
            self.original_viewer.set_crosshair(x, y)
        else:
            self.original_viewer.clear_crosshair()

    def on_original_mouse_left(self):
        self.processed_viewer.clear_crosshair()

    def on_processed_mouse_left(self):
        self.original_viewer.clear_crosshair()

    def on_original_zoom_changed(self, zoom: float):
        if not self.syncing:
            self.syncing = True
            self.processed_viewer.set_zoom(zoom)
            self.syncing = False

    def on_processed_zoom_changed(self, zoom: float):
        if not self.syncing:
            self.syncing = True
            self.original_viewer.set_zoom(zoom)
            self.syncing = False

    def on_original_pan_changed(self, h: int, v: int):
        if not self.syncing:
            self.syncing = True
            self.processed_viewer.set_scroll_position(h, v)
            self.syncing = False

    def on_processed_pan_changed(self, h: int, v: int):
        if not self.syncing:
            self.syncing = True
            self.original_viewer.set_scroll_position(h, v)
            self.syncing = False

    # ========== همگام‌سازی هیستوگرام‌ها ==========

    def on_original_hist_zoom_changed(self, zoom: float):
        if not self.syncing_histograms:
            self.syncing_histograms = True
            self.processed_histogram.set_zoom(zoom)
            self.syncing_histograms = False

    def on_processed_hist_zoom_changed(self, zoom: float):
        if not self.syncing_histograms:
            self.syncing_histograms = True
            self.original_histogram.set_zoom(zoom)
            self.syncing_histograms = False

    def on_original_hist_pan_changed(self, h: int, v: int):
        if not self.syncing_histograms:
            self.syncing_histograms = True
            self.processed_histogram.set_scroll_position(h, v)
            self.syncing_histograms = False

    def on_processed_hist_pan_changed(self, h: int, v: int):
        if not self.syncing_histograms:
            self.syncing_histograms = True
            self.original_histogram.set_scroll_position(h, v)
            self.syncing_histograms = False

    # ========== تنظیمات ==========

    def show_settings(self):
        """نمایش پنجره تنظیمات"""
        dialog = SettingsDialog(self)
        dialog.settings_changed.connect(self.on_settings_changed)
        dialog.exec()

    def on_settings_changed(self, new_settings: dict):
        """اعمال لحظه‌ای تنظیمات (بدون نیاز به ری‌استارت)"""
        # زبان
        lang = new_settings.get("language", self.current_lang)
        if lang != self.current_lang:
            self.current_lang = lang
            self.apply_language()

        # تم
        theme = new_settings.get("theme", self.settings.get("theme", "dark"))
        apply_app_theme(theme)
        # استایل بعضی ویجت‌های ساخته‌شده با stylesheet داخلی را هم دوباره اعمال می‌کنیم
        self.refresh_dynamic_styles()

        # سرعت zoom
        config.ZOOM_WHEEL_FACTOR = self.settings.get_zoom_factor()

        # show hints
        if hasattr(self.control_panel, "set_show_hints"):
            self.control_panel.set_show_hints(self.settings.get("show_hints", True))

    def apply_language(self):
        """اعمال زبان در لحظه (عنوان، لیبل‌ها، جهت، پنل کنترل)"""
        # جهت کلی پنجره
        self.setLayoutDirection(
            Qt.RightToLeft if self.settings.is_rtl() else Qt.LeftToRight
        )

        # عنوان
        self.setWindowTitle(Translations.get("app_title", self.current_lang))

        # برچسب‌های status
        # فیلتر
        self.update_filter_label(getattr(self, "current_filter_key", "original"))

        # فایل
        if self.current_filename:
            self.update_filename_label(self.current_filename)
        else:
            self.filename_label.setText(
                Translations.get("status_file", self.current_lang) + ": -"
            )

        # مختصات
        self.update_mouse_coords(-1, -1)

        # ابعاد (اگر تصویر داریم)
        if self.original_image is not None:
            h, w = self.original_image.shape[:2]
            self.update_dimensions_labels(w, h, w, h)
        else:
            self.dimensions_input_label.setText(
                Translations.get("status_input", self.current_lang) + ": -"
            )
            self.dimensions_output_label.setText(
                Translations.get("status_output", self.current_lang) + ": -"
            )

        self.update_console_title()

        # پنل کنترل
        if hasattr(self.control_panel, "set_language"):
            self.control_panel.set_language(self.current_lang)

        # هرجا متن ثابت داریم بهتره اینجا به‌روزرسانی شود (در صورت نیاز)

    def update_console_styles(self):
        """استایل کنسول را بر اساس تم فعال بازاعمال می‌کند"""
        self.console_text.setStyleSheet(
            f"""
            QTextEdit {{
                background-color: {config.Colors.WIDGET};
                color: {config.Colors.TEXT};
                border: 1px solid {config.Colors.BORDER};
                border-radius: 6px;
                padding: 8px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11px;
            }}
            QTextEdit:focus {{
                border-color: {config.Colors.PRIMARY};
            }}
            QTextEdit::selection {{
                background-color: {config.Colors.PRIMARY};
                color: white;
            }}
            """
        )

    def _format_log_html(self, timestamp: str, message: str, level: str) -> str:
        """ساخت HTML لاگ بر اساس تم فعلی (تا با تعویض تم قابل رندر مجدد باشد)."""
        if level == "info":
            icon = "ℹ️"
            color = config.Colors.PRIMARY
        elif level == "success":
            icon = "✅"
            color = config.Colors.SUCCESS
        elif level == "error":
            icon = "❌"
            color = config.Colors.ERROR
        elif level == "warning":
            icon = "⚠️"
            color = config.Colors.WARNING
        elif level == "processing":
            icon = "⏳"
            color = config.Colors.INFO
        else:
            icon = "📝"
            color = config.Colors.TEXT

        return (
            f'<span style="color: {config.Colors.TEXT_SECONDARY};">[{timestamp}]</span> '
            f'<span style="color: {color}; font-weight: 600;">{icon}</span> '
            f'<span style="color: {config.Colors.TEXT};">{message}</span>'
        )

    def rebuild_console(self):
        """با تغییر تم، لاگ‌ها را دوباره با رنگ‌های جدید رندر می‌کند."""
        if not hasattr(self, "console_text"):
            return
        self.console_text.blockSignals(True)
        try:
            self.console_text.clear()
            for ts, lvl, msg in self._log_entries:
                self.console_text.append(self._format_log_html(ts, msg, lvl))
        finally:
            self.console_text.blockSignals(False)

    def update_console_title(self):
        """عنوان گروه کنسول را با زبان فعلی هماهنگ می‌کند"""
        if hasattr(self, "console_group"):
            self.console_group.setTitle(
                Translations.get("console_title", self.current_lang)
            )

    def refresh_dynamic_styles(self):
        """بازاعمال استایل ویجت‌هایی که استایل داخلی دارند"""
        if hasattr(self, "status_frame"):
            self.update_status_bar_styles()
        if hasattr(self, "original_viewer"):
            self.original_viewer.refresh_styles()
        if hasattr(self, "processed_viewer"):
            self.processed_viewer.refresh_styles()
        if hasattr(self, "console_text"):
            self.update_console_styles()
            # important: existing log lines were rendered with the previous theme colors
            self.rebuild_console()
        self.update_console_title()

    # ========== Status Bar ==========

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
            else:
                child = item.layout()
                if child is not None:
                    self._clear_layout(child)

    def create_status_bar(self):
        """ایجاد نوار وضعیت (یک‌بار)"""
        if getattr(self, "_status_initialized", False):
            return

        self.status_frame = QFrame()
        self.status_frame.setFrameShape(QFrame.StyledPanel)

        self.status_layout = QHBoxLayout(self.status_frame)
        self.status_layout.setContentsMargins(10, 5, 10, 5)
        self.status_layout.setSpacing(15)

        self._status_widgets = {}

        def _vline():
            sep = QFrame()
            sep.setFrameShape(QFrame.VLine)
            sep.setFixedWidth(1)
            # در QSS برای خط عمودی بهتر است background-color استفاده شود
            sep.setStyleSheet(f"background-color: {config.Colors.BORDER};")
            return sep

        def _chip(bg_color: str):
            w = QWidget()
            w.setStyleSheet(
                f"""
                background-color: {bg_color};
                border-radius: 6px;
                padding: 2px;
                """
            )
            lay = QHBoxLayout(w)
            lay.setContentsMargins(8, 4, 8, 4)
            lay.setSpacing(6)
            return w, lay

        # --- Filter chip ---
        self.filter_container, fl = _chip(config.Colors.PRIMARY)
        self.filter_icon = QLabel("🎨")
        self.filter_icon.setStyleSheet(
            "font-size: 14px; background: transparent; padding: 0px;"
        )
        self.filter_label = QLabel("")
        self.filter_label.setStyleSheet(
            "color: white; font-weight: bold; background: transparent; padding: 0px;"
        )
        fl.addWidget(self.filter_icon)
        fl.addWidget(self.filter_label)
        self.status_layout.addWidget(self.filter_container)

        self.sep1 = _vline()
        self.status_layout.addWidget(self.sep1)

        # --- Filename chip ---
        self.filename_container, fnl = _chip(config.Colors.WIDGET)
        self.filename_icon = QLabel("📄")
        self.filename_icon.setStyleSheet(
            "font-size: 14px; background: transparent; padding: 0px;"
        )
        self.filename_label = QLabel("")
        self.filename_label.setStyleSheet("background: transparent; padding: 0px;")
        fnl.addWidget(self.filename_icon)
        fnl.addWidget(self.filename_label)
        self.status_layout.addWidget(self.filename_container)

        self.sep2 = _vline()
        self.status_layout.addWidget(self.sep2)

        # --- Input dims chip ---
        self.dims_input_container, dil = _chip(config.Colors.WIDGET)
        self.dims_input_icon = QLabel("📥")
        self.dims_input_icon.setStyleSheet(
            "font-size: 14px; background: transparent; padding: 0px;"
        )
        self.dimensions_input_label = QLabel("")
        self.dimensions_input_label.setStyleSheet(
            "background: transparent; padding: 0px;"
        )
        dil.addWidget(self.dims_input_icon)
        dil.addWidget(self.dimensions_input_label)
        self.status_layout.addWidget(self.dims_input_container)

        self.sep3 = _vline()
        self.status_layout.addWidget(self.sep3)

        # --- Output dims chip ---
        self.dims_output_container, dol = _chip(config.Colors.WIDGET)
        self.dims_output_icon = QLabel("📤")
        self.dims_output_icon.setStyleSheet(
            "font-size: 14px; background: transparent; padding: 0px;"
        )
        self.dimensions_output_label = QLabel("")
        self.dimensions_output_label.setStyleSheet(
            "background: transparent; padding: 0px;"
        )
        dol.addWidget(self.dims_output_icon)
        dol.addWidget(self.dimensions_output_label)
        self.status_layout.addWidget(self.dims_output_container)

        self.sep4 = _vline()
        self.status_layout.addWidget(self.sep4)

        # --- Coords chip ---
        self.coords_container, cl = _chip(config.Colors.WIDGET)
        self.coords_icon = QLabel("🖱️")
        self.coords_icon.setStyleSheet(
            "font-size: 14px; background: transparent; padding: 0px;"
        )
        self.coords_label = QLabel("")
        self.coords_label.setStyleSheet("background: transparent; padding: 0px;")
        cl.addWidget(self.coords_icon)
        cl.addWidget(self.coords_label)
        self.status_layout.addWidget(self.coords_container)

        self.status_layout.addStretch()

        # Apply initial texts + styles
        self.update_status_bar_texts()
        self.update_status_bar_styles()

        self._status_initialized = True

    def update_status_bar_texts(self):
        """به‌روزرسانی متن‌های نوار وضعیت (برای تغییر زبان)"""
        # Filter label text is updated via update_filter_label
        self.update_filter_label(getattr(self, "current_filter_key", "original"))

        # File
        if getattr(self, "current_filename", ""):
            self.update_filename_label(self.current_filename)
        else:
            self.filename_label.setText(
                Translations.get("status_file", self.current_lang) + ": -"
            )

        # Dims
        if getattr(self, "original_image", None) is not None:
            h, w = self.original_image.shape[:2]
            self.update_dimensions_labels(w, h, w, h)
        else:
            self.dimensions_input_label.setText(
                Translations.get("status_input", self.current_lang) + ": -"
            )
            self.dimensions_output_label.setText(
                Translations.get("status_output", self.current_lang) + ": -"
            )

        # Coords
        self.coords_label.setText(
            Translations.get("status_coords", self.current_lang) + ": -"
        )

    def update_status_bar_styles(self):
        """به‌روزرسانی رنگ‌ها/استایل نوار وضعیت (برای تغییر تم)"""
        self.status_frame.setStyleSheet(
            f"""
            QFrame {{
                background: {config.Colors.PANEL};
                border-top: 2px solid {config.Colors.PRIMARY};
                padding: 8px;
            }}
            QLabel {{
                background: transparent;
                color: {config.Colors.TEXT};
                font-size: 12px;
                padding: 0px;
            }}
            """
        )

        # chips
        self.filter_container.setStyleSheet(
            f"""background-color: {config.Colors.PRIMARY}; border-radius: 6px; padding: 2px;"""
        )
        for w in (
            self.filename_container,
            self.dims_input_container,
            self.dims_output_container,
            self.coords_container,
        ):
            w.setStyleSheet(
                f"""background-color: {config.Colors.WIDGET}; border-radius: 6px; padding: 2px;"""
            )
        for sep in (self.sep1, self.sep2, self.sep3, self.sep4):
            sep.setStyleSheet(f"background-color: {config.Colors.BORDER};")

    def update_mouse_coords(self, x: int, y: int):
        if x >= 0 and y >= 0:
            self.coords_label.setText(
                Translations.get("status_coords", self.current_lang) + f": X={x}, Y={y}"
            )
        else:
            self.coords_label.setText(
                Translations.get("status_coords", self.current_lang) + ": -"
            )

    def update_filter_label(self, filter_name: str):
        self.current_filter_key = filter_name
        display_name = Translations.get_filter_name(filter_name, self.current_lang)
        self.current_filter_name = display_name
        self.filter_label.setText(
            Translations.get("status_filter", self.current_lang) + f": {display_name}"
        )

    def update_filename_label(self, filename: str):
        """بروزرسانی برچسب نام فایل"""
        self.current_filename = filename
        if filename:
            basename = os.path.basename(filename)
            if len(basename) > 30:
                basename = basename[:27] + "..."
            self.filename_label.setText(
                Translations.get("status_file", self.current_lang) + f": {basename}"
            )
        else:
            self.filename_label.setText(
                Translations.get("status_file", self.current_lang) + ": -"
            )

    def update_dimensions_labels(
        self, input_w: int = 0, input_h: int = 0, output_w: int = 0, output_h: int = 0
    ):
        """بروزرسانی برچسب‌های ابعاد"""
        if input_w > 0 and input_h > 0:
            self.dimensions_input_label.setText(
                Translations.get("status_input", self.current_lang)
                + f": {input_w} × {input_h}"
            )
        else:
            self.dimensions_input_label.setText(
                Translations.get("status_input", self.current_lang) + ": -"
            )

        if output_w > 0 and output_h > 0:
            self.dimensions_output_label.setText(
                Translations.get("status_output", self.current_lang)
                + f": {output_w} × {output_h}"
            )
        else:
            self.dimensions_output_label.setText(
                Translations.get("status_output", self.current_lang) + ": -"
            )

    # ========== عملیات فایل ==========

    def load_image(self):
        """بارگذاری تصویر"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            Translations.get("load_image", self.current_lang),
            self.settings.get("last_directory", ""),
            "Images (*.png *.jpg *.jpeg *.bmp *.tiff)",
        )

        if filename:
            self.log(f"Loading image: {os.path.basename(filename)}", "info")

            image = ImageManager.load_image(filename)

            if image is not None:
                self.original_image = image
                self.current_image = image.copy()

                # نمایش
                self.original_viewer.set_image(self.original_image)
                self.processed_viewer.set_image(self.current_image)
                self.original_histogram.set_image(self.original_image)
                self.processed_histogram.set_image(self.current_image)

                # ذخیره مسیر
                self.settings.set("last_directory", os.path.dirname(filename))
                self.settings.save()

                # بروزرسانی UI
                self.update_filename_label(filename)
                height, width = image.shape[:2]
                self.update_dimensions_labels(width, height, width, height)
                self.update_filter_label("original")

                # ✅ Log موفقیت
                self.log(
                    f"Image loaded successfully: {width}×{height} pixels", "success"
                )

            else:
                # ✅ Log خطا
                self.log(f"Failed to load image: {os.path.basename(filename)}", "error")

                QMessageBox.critical(
                    self,
                    Translations.get("msg_error", self.current_lang),
                    "Error loading image!",
                )

    def save_image(self):
        """ذخیره تصویر"""
        if self.current_image is None:
            self.log("No image to save", "warning")
            QMessageBox.warning(
                self,
                Translations.get("msg_warning", self.current_lang),
                Translations.get("msg_no_image", self.current_lang),
            )
            return

        default_format = self.settings.get("default_format", "PNG")
        filter_str = f"{default_format} (*.{default_format.lower()});;All Files (*.*)"

        filename, _ = QFileDialog.getSaveFileName(
            self,
            Translations.get("save_image", self.current_lang),
            self.settings.get("last_directory", ""),
            filter_str,
        )

        if filename:
            self.log(f"Saving image: {os.path.basename(filename)}", "info")

            quality = self.settings.get_quality_value()
            if ImageManager.save_image(filename, self.current_image, quality=quality):
                self.log(
                    f"Image saved successfully: {os.path.basename(filename)}", "success"
                )

                QMessageBox.information(
                    self,
                    Translations.get("msg_success", self.current_lang),
                    Translations.get("msg_image_saved", self.current_lang),
                )
            else:
                self.log(f"Failed to save image: {os.path.basename(filename)}", "error")

                QMessageBox.critical(
                    self,
                    Translations.get("msg_error", self.current_lang),
                    "Error saving image!",
                )

    def _cleanup_thread(self, thread):
        """Cleanup a finished/cancelled worker thread safely."""
        try:
            if thread in self._retired_threads:
                self._retired_threads.remove(thread)
        finally:
            thread.deleteLater()

    def apply_filter(self, filter_name: str, params: dict):
        """اعمال فیلتر"""
        if self.original_image is None:
            self.log("No image loaded to apply filter", "warning")
            return

        self.update_filter_label(filter_name)

        if filter_name == "original":
            self.log("Reset to original image", "info")
            self.current_image = self.original_image.copy()
            self.processed_viewer.set_image(self.current_image)
            self.processed_histogram.set_image(self.current_image)
            return

        display_name = Translations.get_filter_name(filter_name, self.current_lang)
        self.log(f"Applying filter: {display_name}...", "info")
        # Cancel previous processing safely (avoid terminate(), which can crash / leak)
        if self.processing_thread and self.processing_thread.isRunning():
            old = self.processing_thread
            old.stop()  # prevents emitting finished/error in our ProcessingThread.run()

            # Keep a reference until the thread naturally exits, then clean it up.
            self._retired_threads.append(old)
            old.finished.connect(lambda: self._cleanup_thread(old))
            old.error.connect(lambda *_: self._cleanup_thread(old))

        self.processing_thread = ProcessingThread(
            self.original_image, filter_name, params
        )

        self.processing_thread.result.connect(self.on_processing_finished)
        self.processing_thread.error.connect(self.on_processing_error)
        self.processing_thread.start()

        self.log(f"Processing started for '{display_name}'", "processing")

    def on_processing_finished(self, processed_image):
        """پایان پردازش"""
        self.current_image = processed_image
        self.processed_viewer.set_image(processed_image)
        self.processed_histogram.set_image(processed_image)

        # ✅ بروزرسانی سایز output
        output_h, output_w = processed_image.shape[:2]
        if self.original_image is not None:
            input_h, input_w = self.original_image.shape[:2]
            self.update_dimensions_labels(input_w, input_h, output_w, output_h)

            if input_w == output_w and input_h == output_h:
                self.log(
                    f"✓ Filter applied successfully! Output: {output_w}×{output_h}",
                    "success",
                )
            else:
                self.log(
                    f"✓ Filter applied! Input: {input_w}×{input_h} → Output: {output_w}×{output_h}",
                    "success",
                )

        else:
            self.log(f"Filter applied successfully ({output_w}×{output_h})", "success")

    def on_processing_error(self, error_message: str):
        """خطا در پردازش"""
        self.log(f"Processing error: {error_message}", "error")
        QMessageBox.critical(
            self,
            Translations.get("msg_error", self.current_lang),
            f"Processing error: {error_message}",
        )

    def reset_image(self):
        """بازنشانی"""
        if self.original_image is not None:
            self.log("Resetting to original image", "info")

            self.current_image = self.original_image.copy()
            self.processed_viewer.set_image(self.current_image)
            self.processed_histogram.set_image(self.current_image)
            self.update_filter_label("original")

            self.log("Image reset successfully", "success")

    # ========== Zoom ==========

    def zoom_in_viewers(self):
        current_tab = self.view_tabs.currentIndex()
        if current_tab == 0:
            self.original_viewer.zoom_in()
        elif current_tab == 1:
            self.original_histogram.zoom_in()

    def zoom_out_viewers(self):
        current_tab = self.view_tabs.currentIndex()
        if current_tab == 0:
            self.original_viewer.zoom_out()
        elif current_tab == 1:
            self.original_histogram.zoom_out()

    def zoom_reset_viewers(self):
        current_tab = self.view_tabs.currentIndex()
        if current_tab == 0:
            self.original_viewer.reset_zoom()
        elif current_tab == 1:
            self.original_histogram.reset_zoom()

    def show_custom_kernel_dialog(self):
        from ui.custom_kernel_dialog import CustomKernelDialog

        self.log("Opening Custom Kernel dialog", "info")

        dialog = CustomKernelDialog(self)
        dialog.kernel_ready.connect(self.apply_custom_kernel)
        dialog.exec()

    def apply_custom_kernel(self, kernel: np.ndarray, normalize: bool, padding: str):
        """اعمال Custom Kernel"""
        if self.original_image is None:
            self.log("No image loaded for custom kernel", "warning")
            return

        self.log(
            f"Applying custom kernel ({kernel.shape[0]}×{kernel.shape[1]}, "
            f"normalize={normalize}, padding={padding})",
            "info",
        )

        params = {
            "kernel": kernel,
            "normalize": normalize,
            "padding": padding,
        }

        self.apply_filter("conv_custom", params)

    def show_transformation_dialog(self):
        if self.original_image is None:
            self.log("No image loaded for transformation", "warning")
            QMessageBox.warning(
                self,
                Translations.get("msg_warning", self.current_lang),
                "Please load an image first!",
            )
            return

        self.log("Opening Transformation dialog", "info")
        dialog = TransformationDialog(self)
        dialog.transformation_ready.connect(self.apply_transformation)
        dialog.exec()

    def apply_transformation(self, method: str, params: dict):
        if self.original_image is None:
            self.log("No image loaded for transformation", "warning")
            return

        rotation = params.get("rotation", 0)
        scale = params.get("scale", 1.0)
        brightness = params.get("brightness", 0)

        method_name = {
            "transform_direct": "Direct Map",
            "transform_inverse_nn": "Inverse Map (NN)",
            "transform_inverse_bilinear": "Inverse Map (Bilinear)",
            "transform_inverse_bicubic": "Inverse Map (Bicubic)",
        }.get(method, method)

        self.log(
            f"Applying {method_name}: R={rotation}°, S={scale:.1f}x, B={brightness:+d}",
            "info",
        )

        self.apply_filter(method, params)

    def log(self, message: str, level: str = "info"):
        import datetime

        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        # keep entries so we can re-render them when theme changes
        try:
            self._log_entries.append((timestamp, level, message))
            # optional cap to avoid infinite growth
            if len(self._log_entries) > 5000:
                self._log_entries = self._log_entries[-3000:]
        except Exception:
            pass

        self.console_text.append(self._format_log_html(timestamp, message, level))

        # cursor = self.console_text.textCursor()
        # cursor.movePosition(QTextCursor.MoveOperation.End)
        # self.console_text.setTextCursor(cursor)

        scrollbar = self.console_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def closeEvent(self, event):
        """تایید خروج"""
        try:
            if self.settings.get("confirm_exit", True):
                reply = QMessageBox.question(
                    self,
                    Translations.get("app_title", self.current_lang),
                    Translations.get("msg_exit_confirm", self.current_lang),
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No,
                )
                if reply != QMessageBox.Yes:
                    event.ignore()
                    return
        except Exception:
            pass
        event.accept()
