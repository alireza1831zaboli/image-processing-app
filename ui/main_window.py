"""
پنجره اصلی نهایی با سیستم تنظیمات کامل
Final Main Window with Complete Settings System
"""

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
)
from PySide6.QtCore import Qt
import config
from ui.image_viewer import ImageViewer
from ui.synced_histogram_viewer import SyncedHistogramViewer
from ui.control_panel import ControlPanel
from ui.settings_dialog import SettingsDialog
from ui.styles import get_main_stylesheet
from core.image_manager import ImageManager
from core.processing_thread import ProcessingThread
from translations import Translations
from settings_manager import get_settings
import os


class MainWindow(QMainWindow):
    """پنجره اصلی"""

    def __init__(self):
        super().__init__()

        # مدیریت تنظیمات
        self.settings = get_settings()
        self.current_lang = self.settings.get("language", "fa")

        # عنوان پنجره
        self.setWindowTitle(Translations.get("app_title", self.current_lang))
        self.setGeometry(100, 100, config.WINDOW_WIDTH, config.WINDOW_HEIGHT)

        # متغیرها
        self.original_image = None
        self.current_image = None
        self.processing_thread = None
        self.current_filter_name = Translations.get(
            "filter_original", self.current_lang
        )
        self.current_filename = ""

        # برای جلوگیری از loop بی‌نهایت
        self.syncing = False
        self.syncing_histograms = False

        self.setup_ui()
        self.setStyleSheet(get_main_stylesheet())

    def setup_ui(self):
        """ساخت UI"""
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Layout اصلی
        content_layout = QHBoxLayout()
        content_layout.setSpacing(10)
        content_layout.setContentsMargins(10, 10, 10, 5)

        # پنل کنترل
        self.control_panel = ControlPanel()
        self.control_panel.setFixedWidth(330)
        self.control_panel.filter_changed.connect(self.apply_filter)
        self.control_panel.load_clicked.connect(self.load_image)
        self.control_panel.save_clicked.connect(self.save_image)
        self.control_panel.reset_clicked.connect(self.reset_image)
        self.control_panel.settings_clicked.connect(self.show_settings)  # جدید!
        self.control_panel.zoom_in_clicked.connect(self.zoom_in_viewers)
        self.control_panel.zoom_out_clicked.connect(self.zoom_out_viewers)
        self.control_panel.zoom_reset_clicked.connect(self.zoom_reset_viewers)
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

        # نوار وضعیت
        self.create_status_bar()
        main_layout.addWidget(self.status_frame)

    def create_image_viewers(self):
        """ایجاد viewer های تصویر"""
        viewers_layout = QHBoxLayout()
        viewers_layout.setSpacing(10)

        # تصویر اصلی
        original_group = QGroupBox(
            Translations.get("original_image", self.current_lang)
        )
        original_layout = QVBoxLayout()
        self.original_viewer = ImageViewer()
        self.original_viewer.sync_enabled = True
        self.original_viewer.mouse_moved.connect(self.on_original_mouse_moved)
        self.original_viewer.mouse_left.connect(self.on_original_mouse_left)
        self.original_viewer.zoom_changed.connect(self.on_original_zoom_changed)
        self.original_viewer.pan_changed.connect(self.on_original_pan_changed)
        original_layout.addWidget(self.original_viewer)
        original_group.setLayout(original_layout)
        viewers_layout.addWidget(original_group)

        # تصویر پردازش شده
        processed_group = QGroupBox(
            Translations.get("processed_image", self.current_lang)
        )
        processed_layout = QVBoxLayout()
        self.processed_viewer = ImageViewer()
        self.processed_viewer.sync_enabled = True
        self.processed_viewer.mouse_moved.connect(self.on_processed_mouse_moved)
        self.processed_viewer.mouse_left.connect(self.on_processed_mouse_left)
        self.processed_viewer.zoom_changed.connect(self.on_processed_zoom_changed)
        self.processed_viewer.pan_changed.connect(self.on_processed_pan_changed)
        processed_layout.addWidget(self.processed_viewer)
        processed_group.setLayout(processed_layout)
        viewers_layout.addWidget(processed_group)

        return viewers_layout

    def create_histogram_viewers(self):
        """ایجاد viewer های هیستوگرام"""
        viewers_layout = QHBoxLayout()
        viewers_layout.setSpacing(10)

        # هیستوگرام اصلی
        original_hist_group = QGroupBox(
            Translations.get("original_histogram", self.current_lang)
        )
        original_hist_layout = QVBoxLayout()
        self.original_histogram = SyncedHistogramViewer()
        self.original_histogram.sync_enabled = True
        self.original_histogram.zoom_changed.connect(self.on_original_hist_zoom_changed)
        self.original_histogram.pan_changed.connect(self.on_original_hist_pan_changed)
        original_hist_layout.addWidget(self.original_histogram)
        original_hist_group.setLayout(original_hist_layout)
        viewers_layout.addWidget(original_hist_group)

        # هیستوگرام پردازش شده
        processed_hist_group = QGroupBox(
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
        processed_hist_group.setLayout(processed_hist_layout)
        viewers_layout.addWidget(processed_hist_group)

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
        dialog.settings_applied.connect(self.on_settings_applied)
        dialog.exec()

    def on_settings_applied(self, new_settings: dict):
        """پس از اعمال تنظیمات"""
        # اگر زبان تغییر کرد
        if new_settings.get("language") != self.current_lang:
            QMessageBox.information(
                self,
                Translations.get("msg_success", new_settings.get("language")),
                "Please restart the application for language changes to take effect.",
            )
            self.current_lang = new_settings.get("language")

        # اگر سرعت zoom تغییر کرد
        # می‌تونیم config رو update کنیم
        zoom_factor = self.settings.get_zoom_factor()
        config.ZOOM_WHEEL_FACTOR = zoom_factor

        self.statusBar().showMessage(
            "✓ " + Translations.get("msg_success", self.current_lang), 3000
        )

    # ========== Status Bar ==========

    def create_status_bar(self):
        """ایجاد نوار وضعیت"""
        self.status_frame = QFrame()
        self.status_frame.setFrameShape(QFrame.StyledPanel)
        self.status_frame.setStyleSheet(
            f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {config.Colors.PANEL},
                    stop:1 {config.Colors.WIDGET});
                border-top: 2px solid {config.Colors.PRIMARY};
                padding: 8px;
            }}
            QLabel {{
                background: transparent;
                color: {config.Colors.TEXT};
                font-size: 12px;
                padding: 4px 12px;
                border-radius: 4px;
            }}
        """
        )

        status_layout = QHBoxLayout(self.status_frame)
        status_layout.setContentsMargins(10, 5, 10, 5)
        status_layout.setSpacing(15)

        # فیلتر
        filter_container = QWidget()
        filter_container.setStyleSheet(
            f"""
            background-color: {config.Colors.PRIMARY};
            border-radius: 6px;
            padding: 2px;
        """
        )
        filter_layout = QHBoxLayout(filter_container)
        filter_layout.setContentsMargins(8, 4, 8, 4)
        filter_icon = QLabel("🎨")
        filter_icon.setStyleSheet(
            "font-size: 14px; background: transparent; padding: 0px;"
        )
        self.filter_label = QLabel(
            Translations.get("status_filter", self.current_lang)
            + ": "
            + Translations.get("filter_original", self.current_lang)
        )
        self.filter_label.setStyleSheet(
            "color: white; font-weight: bold; background: transparent; padding: 0px;"
        )
        filter_layout.addWidget(filter_icon)
        filter_layout.addWidget(self.filter_label)
        status_layout.addWidget(filter_container)

        # جداکننده
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.VLine)
        sep1.setStyleSheet(f"color: {config.Colors.BORDER};")
        status_layout.addWidget(sep1)

        # فایل
        filename_container = QWidget()
        filename_container.setStyleSheet(
            f"""
            background-color: {config.Colors.WIDGET};
            border-radius: 6px;
            padding: 2px;
        """
        )
        filename_layout = QHBoxLayout(filename_container)
        filename_layout.setContentsMargins(8, 4, 8, 4)
        filename_icon = QLabel("📄")
        filename_icon.setStyleSheet(
            "font-size: 14px; background: transparent; padding: 0px;"
        )
        self.filename_label = QLabel(
            Translations.get("status_file", self.current_lang) + ": -"
        )
        self.filename_label.setStyleSheet("background: transparent; padding: 0px;")
        filename_layout.addWidget(filename_icon)
        filename_layout.addWidget(self.filename_label)
        status_layout.addWidget(filename_container)

        # جداکننده
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.VLine)
        sep2.setStyleSheet(f"color: {config.Colors.BORDER};")
        status_layout.addWidget(sep2)

        # ابعاد
        dims_container = QWidget()
        dims_container.setStyleSheet(
            f"""
            background-color: {config.Colors.WIDGET};
            border-radius: 6px;
            padding: 2px;
        """
        )
        dims_layout = QHBoxLayout(dims_container)
        dims_layout.setContentsMargins(8, 4, 8, 4)
        dims_icon = QLabel("📐")
        dims_icon.setStyleSheet(
            "font-size: 14px; background: transparent; padding: 0px;"
        )
        self.dimensions_label = QLabel(
            Translations.get("status_dimensions", self.current_lang) + ": -"
        )
        self.dimensions_label.setStyleSheet("background: transparent; padding: 0px;")
        dims_layout.addWidget(dims_icon)
        dims_layout.addWidget(self.dimensions_label)
        status_layout.addWidget(dims_container)

        # جداکننده
        sep3 = QFrame()
        sep3.setFrameShape(QFrame.VLine)
        sep3.setStyleSheet(f"color: {config.Colors.BORDER};")
        status_layout.addWidget(sep3)

        # مختصات
        coords_container = QWidget()
        coords_container.setStyleSheet(
            f"""
            background-color: {config.Colors.WIDGET};
            border-radius: 6px;
            padding: 2px;
        """
        )
        coords_layout = QHBoxLayout(coords_container)
        coords_layout.setContentsMargins(8, 4, 8, 4)
        coords_icon = QLabel("🖱️")
        coords_icon.setStyleSheet(
            "font-size: 14px; background: transparent; padding: 0px;"
        )
        self.coords_label = QLabel(
            Translations.get("status_coords", self.current_lang) + ": -"
        )
        self.coords_label.setStyleSheet("background: transparent; padding: 0px;")
        coords_layout.addWidget(coords_icon)
        coords_layout.addWidget(self.coords_label)
        status_layout.addWidget(coords_container)

        status_layout.addStretch()

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
        display_name = Translations.get_filter_name(filter_name, self.current_lang)
        self.current_filter_name = display_name
        self.filter_label.setText(
            Translations.get("status_filter", self.current_lang) + f": {display_name}"
        )

    def update_filename_label(self, filename: str):
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

    def update_dimensions_label(self, width: int, height: int):
        if width > 0 and height > 0:
            self.dimensions_label.setText(
                Translations.get("status_dimensions", self.current_lang)
                + f": {width} × {height}"
            )
        else:
            self.dimensions_label.setText(
                Translations.get("status_dimensions", self.current_lang) + ": -"
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

                # به‌روزرسانی UI
                self.update_filename_label(filename)
                height, width = image.shape[:2]
                self.update_dimensions_label(width, height)
                self.update_filter_label("original")

                self.statusBar().showMessage(
                    "✓ " + Translations.get("msg_image_loaded", self.current_lang), 3000
                )
            else:
                QMessageBox.critical(
                    self,
                    Translations.get("msg_error", self.current_lang),
                    "Error loading image!",
                )
                self.statusBar().showMessage(
                    "✗ " + Translations.get("msg_error", self.current_lang), 3000
                )

    def save_image(self):
        """ذخیره تصویر"""
        if self.current_image is None:
            QMessageBox.warning(
                self,
                Translations.get("msg_warning", self.current_lang),
                Translations.get("msg_no_image", self.current_lang),
            )
            return

        # فرمت پیشفرض از تنظیمات
        default_format = self.settings.get("default_format", "PNG")
        filter_str = f"{default_format} (*.{default_format.lower()});;All Files (*.*)"

        filename, _ = QFileDialog.getSaveFileName(
            self,
            Translations.get("save_image", self.current_lang),
            self.settings.get("last_directory", ""),
            filter_str,
        )

        if filename:
            # استفاده از کیفیت از تنظیمات
            quality = self.settings.get_quality_value()

            if ImageManager.save_image(filename, self.current_image):
                self.statusBar().showMessage(
                    "✓ " + Translations.get("msg_image_saved", self.current_lang), 3000
                )
                QMessageBox.information(
                    self,
                    Translations.get("msg_success", self.current_lang),
                    Translations.get("msg_image_saved", self.current_lang),
                )
            else:
                self.statusBar().showMessage(
                    "✗ " + Translations.get("msg_error", self.current_lang), 3000
                )
                QMessageBox.critical(
                    self,
                    Translations.get("msg_error", self.current_lang),
                    "Error saving image!",
                )

    def apply_filter(self, filter_name: str, params: dict):
        """اعمال فیلتر"""
        if self.original_image is None:
            return

        self.update_filter_label(filter_name)

        if filter_name == "original":
            self.current_image = self.original_image.copy()
            self.processed_viewer.set_image(self.current_image)
            self.processed_histogram.set_image(self.current_image)
            self.statusBar().showMessage(
                "✓ " + Translations.get("filter_original", self.current_lang), 2000
            )
            return

        if self.processing_thread and self.processing_thread.isRunning():
            self.processing_thread.terminate()
            self.processing_thread.wait()

        self.processing_thread = ProcessingThread(
            self.original_image, filter_name, params
        )
        self.processing_thread.finished.connect(self.on_processing_finished)
        self.processing_thread.error.connect(self.on_processing_error)
        self.processing_thread.start()

        self.statusBar().showMessage(
            f"⏳ {Translations.get('msg_processing', self.current_lang)}...", 0
        )

    def on_processing_finished(self, processed_image):
        """پایان پردازش"""
        self.current_image = processed_image
        self.processed_viewer.set_image(processed_image)
        self.processed_histogram.set_image(processed_image)
        self.statusBar().showMessage(
            f"✓ {Translations.get('msg_filter_applied', self.current_lang)}", 3000
        )

    def on_processing_error(self, error_message: str):
        """خطا در پردازش"""
        self.statusBar().showMessage(f"✗ {error_message}", 5000)
        QMessageBox.critical(
            self,
            Translations.get("msg_error", self.current_lang),
            f"Processing error: {error_message}",
        )

    def reset_image(self):
        """بازنشانی"""
        if self.original_image is not None:
            self.current_image = self.original_image.copy()
            self.processed_viewer.set_image(self.current_image)
            self.processed_histogram.set_image(self.current_image)
            self.update_filter_label("original")
            self.statusBar().showMessage(
                "✓ " + Translations.get("msg_reset", self.current_lang), 3000
            )

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
