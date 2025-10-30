"""
پنجره اصلی برنامه
Main Window
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
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor

import config
from ui.image_viewer import ImageViewer
from ui.control_panel import ControlPanel
from ui.styles import get_main_stylesheet
from core.image_manager import ImageManager
from core.processing_thread import ProcessingThread


class MainWindow(QMainWindow):
    """پنجره اصلی"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(config.WINDOW_TITLE)
        self.setGeometry(100, 100, config.WINDOW_WIDTH, config.WINDOW_HEIGHT)

        # متغیرها
        self.original_image = None
        self.current_image = None
        self.processing_thread = None

        self.setup_ui()
        self.setStyleSheet(get_main_stylesheet())

    def setup_ui(self):
        """ساخت UI"""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)

        # پنل کنترل
        self.control_panel = ControlPanel()
        self.control_panel.filter_changed.connect(self.apply_filter)
        self.control_panel.load_clicked.connect(self.load_image)
        self.control_panel.save_clicked.connect(self.save_image)
        self.control_panel.reset_clicked.connect(self.reset_image)
        main_layout.addWidget(self.control_panel, 1)

        # پنل تصاویر
        image_panel = self.create_image_panel()
        main_layout.addWidget(image_panel, 3)

    def create_image_panel(self):
        """پنل نمایش تصاویر"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        title = QLabel("نمایش تصاویر")
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # تصاویر
        images_layout = QHBoxLayout()

        # تصویر اصلی
        original_group = QGroupBox("تصویر اصلی")
        original_layout = QVBoxLayout(original_group)
        self.original_viewer = ImageViewer()
        original_layout.addWidget(self.original_viewer)
        images_layout.addWidget(original_group)

        # تصویر پردازش شده
        processed_group = QGroupBox("تصویر پردازش شده")
        processed_layout = QVBoxLayout(processed_group)
        self.processed_viewer = ImageViewer()
        processed_layout.addWidget(self.processed_viewer)
        images_layout.addWidget(processed_group)

        layout.addLayout(images_layout)

        # نوار وضعیت
        self.status_label = QLabel("آماده - در انتظار بارگذاری تصویر")
        self.status_label.setStyleSheet(
            f"""
            padding: 10px; 
            background-color: #1e1e1e; 
            color: {config.Colors.SUCCESS}; 
            border-radius: 5px;
        """
        )
        layout.addWidget(self.status_label)

        return panel

    def load_image(self):
        """بارگذاری تصویر"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "انتخاب تصویر", "", config.SUPPORTED_FORMATS
        )

        if file_path:
            self.original_image = ImageManager.load_image(file_path)
            if self.original_image is not None:
                self.current_image = self.original_image.copy()
                self.original_viewer.set_image(self.original_image)
                self.processed_viewer.set_image(self.current_image)
                self.update_status("تصویر بارگذاری شد", config.Colors.SUCCESS)
            else:
                self.update_status("خطا در بارگذاری", config.Colors.ERROR)

    def apply_filter(self, filter_name, params):
        """اعمال فیلتر"""
        if self.original_image is None:
            self.update_status("لطفاً ابتدا تصویر بارگذاری کنید", config.Colors.WARNING)
            return

        self.update_status("در حال پردازش...", config.Colors.WARNING)

        # پردازش در thread
        self.processing_thread = ProcessingThread(
            self.original_image, filter_name, params
        )
        self.processing_thread.finished.connect(self.on_processing_finished)
        self.processing_thread.error.connect(self.on_processing_error)
        self.processing_thread.start()

    def on_processing_finished(self, result):
        """پس از پردازش"""
        self.current_image = result
        self.processed_viewer.set_image(self.current_image)
        self.update_status("پردازش با موفقیت انجام شد ✓", config.Colors.SUCCESS)

    def on_processing_error(self, error):
        """خطا در پردازش"""
        self.update_status(f"خطا: {error}", config.Colors.ERROR)

    def reset_image(self):
        """بازگشت به اصل"""
        if self.original_image is not None:
            self.current_image = self.original_image.copy()
            self.processed_viewer.set_image(self.current_image)
            self.update_status("بازگشت به تصویر اصلی", config.Colors.INFO)

    def save_image(self):
        """ذخیره تصویر"""
        if self.current_image is None:
            self.update_status(
                "هیچ تصویری برای ذخیره وجود ندارد", config.Colors.WARNING
            )
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "ذخیره تصویر", "", "PNG (*.png);;JPEG (*.jpg);;TIFF (*.tiff)"
        )

        if file_path:
            success = ImageManager.save_image(file_path, self.current_image)
            if success:
                self.update_status("تصویر ذخیره شد", config.Colors.SUCCESS)
            else:
                self.update_status("خطا در ذخیره", config.Colors.ERROR)

    def zoom_in(self):
        """Zoom in"""
        self.processed_viewer.zoom_in()

    def zoom_out(self):
        """Zoom out"""
        self.processed_viewer.zoom_out()

    def reset_zoom(self):
        """Reset zoom"""
        self.processed_viewer.reset_zoom()

    def update_status(self, message, color):
        """به‌روزرسانی وضعیت"""
        self.status_label.setText(message)
        self.status_label.setStyleSheet(
            f"""
            padding: 10px;
            background-color: #1e1e1e;
            color: {color};
            border-radius: 5px;
        """
        )
