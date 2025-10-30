"""
ویوئر تصویر با قابلیت Zoom و Pan
Image Viewer with Zoom and Pan
"""

import numpy as np
from PySide6.QtWidgets import QLabel, QScrollArea
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QImage, QPixmap, QCursor
import config


class ImageViewer(QScrollArea):
    """ویوئر تصویر با قابلیت zoom و pan"""

    def __init__(self):
        super().__init__()

        # ویجت نمایش تصویر
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet(
            f"""
            QLabel {{
                background-color: {config.Colors.IMAGE_VIEWER_BG};
                border: 2px solid {config.Colors.IMAGE_VIEWER_BORDER};
                border-radius: 8px;
            }}
        """
        )

        self.setWidget(self.image_label)
        self.setWidgetResizable(False)
        self.setAlignment(Qt.AlignCenter)

        # متغیرهای zoom و pan
        self.zoom_factor = 1.0
        self.original_pixmap = None
        self.is_panning = False
        self.pan_start_pos = QPoint()

        # تنظیمات نوار اسکرول
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.setMinimumSize(400, 400)

    def set_image(self, image: np.ndarray):
        """نمایش تصویر numpy در viewer"""
        if image is None or image.size == 0:
            return

        try:
            # تبدیل numpy array به QImage
            if len(image.shape) == 2:
                height, width = image.shape
                bytes_per_line = width
                q_image = QImage(
                    image.data, width, height, bytes_per_line, QImage.Format_Grayscale8
                )
            else:
                height, width, channels = image.shape
                bytes_per_line = channels * width
                q_image = QImage(
                    image.data, width, height, bytes_per_line, QImage.Format_BGR888
                )

            # ذخیره pixmap اصلی
            self.original_pixmap = QPixmap.fromImage(q_image)

            # نمایش با zoom فعلی
            self.update_zoom()

        except Exception as e:
            print(f"Error displaying image: {e}")

    def update_zoom(self):
        """به‌روزرسانی نمایش با zoom فعلی"""
        if self.original_pixmap is None:
            return

        # محاسبه اندازه جدید
        new_size = self.original_pixmap.size() * self.zoom_factor

        # Scale کردن تصویر
        scaled_pixmap = self.original_pixmap.scaled(
            new_size, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )

        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.resize(scaled_pixmap.size())

    def wheelEvent(self, event):
        """Zoom با mouse wheel"""
        if self.original_pixmap is None:
            return

        # محاسبه zoom جدید
        if event.angleDelta().y() > 0:
            self.zoom_factor *= config.ZOOM_WHEEL_FACTOR
        else:
            self.zoom_factor /= config.ZOOM_WHEEL_FACTOR

        # محدود کردن zoom
        self.zoom_factor = max(config.ZOOM_MIN, min(config.ZOOM_MAX, self.zoom_factor))

        # به‌روزرسانی نمایش
        self.update_zoom()

    def mousePressEvent(self, event):
        """شروع pan با کلیک و نگه داشتن"""
        if event.button() == Qt.LeftButton and config.PAN_ENABLED:
            self.is_panning = True
            self.pan_start_pos = event.pos()
            self.setCursor(QCursor(Qt.ClosedHandCursor))

    def mouseMoveEvent(self, event):
        """حرکت تصویر با drag"""
        if self.is_panning:
            # محاسبه تغییر مکان
            delta = event.pos() - self.pan_start_pos
            self.pan_start_pos = event.pos()

            # حرکت اسکرول بارها
            h_bar = self.horizontalScrollBar()
            v_bar = self.verticalScrollBar()

            h_bar.setValue(h_bar.value() - delta.x())
            v_bar.setValue(v_bar.value() - delta.y())

    def mouseReleaseEvent(self, event):
        """پایان pan"""
        if event.button() == Qt.LeftButton:
            self.is_panning = False
            self.setCursor(QCursor(Qt.ArrowCursor))

    def reset_zoom(self):
        """بازگشت zoom به حالت اولیه"""
        self.zoom_factor = 1.0
        self.update_zoom()

    def zoom_in(self):
        """Zoom in"""
        self.zoom_factor *= config.ZOOM_WHEEL_FACTOR
        self.zoom_factor = min(config.ZOOM_MAX, self.zoom_factor)
        self.update_zoom()

    def zoom_out(self):
        """Zoom out"""
        self.zoom_factor /= config.ZOOM_WHEEL_FACTOR
        self.zoom_factor = max(config.ZOOM_MIN, self.zoom_factor)
        self.update_zoom()

    def fit_to_window(self):
        """تنظیم اندازه به اندازه پنجره"""
        if self.original_pixmap is None:
            return

        # محاسبه zoom برای fit کردن
        view_size = self.viewport().size()
        pixmap_size = self.original_pixmap.size()

        width_ratio = view_size.width() / pixmap_size.width()
        height_ratio = view_size.height() / pixmap_size.height()

        self.zoom_factor = min(width_ratio, height_ratio) * 0.95
        self.update_zoom()
