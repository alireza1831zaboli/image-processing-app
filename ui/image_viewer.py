"""
ویوئر تصویر با قابلیت Zoom و Pan
Image Viewer with Zoom and Pan
"""

import numpy as np
from PySide6.QtWidgets import QLabel, QScrollArea
from PySide6.QtCore import Qt, QPoint, Signal, QPointF
from PySide6.QtGui import QImage, QPixmap, QCursor, QMouseEvent, QPainter, QPen, QColor
import config


class ImageLabel(QLabel):
    """QLabel سفارشی با قابلیت نمایش crosshair"""

    def __init__(self):
        super().__init__()
        self.crosshair_pos = None  # موقعیت crosshair در مختصات تصویر اصلی
        self.zoom_factor = 1.0

    def set_crosshair(self, x: int, y: int):
        """تنظیم موقعیت crosshair"""
        if x >= 0 and y >= 0:
            self.crosshair_pos = QPoint(x, y)
        else:
            self.crosshair_pos = None
        self.update()  # باعث فراخوانی paintEvent می‌شود

    def clear_crosshair(self):
        """حذف crosshair"""
        self.crosshair_pos = None
        self.update()

    def paintEvent(self, event):
        """رسم تصویر و crosshair"""
        super().paintEvent(event)

        if self.crosshair_pos and self.pixmap() and not self.pixmap().isNull():
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)

            # محاسبه موقعیت crosshair با zoom
            x = int(self.crosshair_pos.x() * self.zoom_factor)
            y = int(self.crosshair_pos.y() * self.zoom_factor)

            # رسم دایره در مرکز
            pen = QPen(QColor(255, 0, 0, 200))  # قرمز شفاف
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawEllipse(QPoint(x, y), 8, 8)

            # رسم خطوط متقاطع
            pen.setStyle(Qt.DashLine)
            painter.setPen(pen)

            # خط عمودی
            painter.drawLine(x, 0, x, self.height())
            # خط افقی
            painter.drawLine(0, y, self.width(), y)

            painter.end()


class ImageViewer(QScrollArea):
    """ویوئر تصویر با قابلیت zoom و pan"""

    # سیگنال‌ها
    mouse_moved = Signal(int, int)  # x, y در تصویر اصلی
    mouse_left = Signal()  # موس از viewer خارج شد
    zoom_changed = Signal(float)  # zoom factor تغییر کرد
    pan_changed = Signal(int, int)  # scroll position تغییر کرد

    def __init__(self):
        super().__init__()

        # ویجت نمایش تصویر (با قابلیت crosshair)
        self.image_label = ImageLabel()
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

        # متغیر برای نگهداری ابعاد تصویر اصلی
        self.original_image_size = None

        # برای همگام‌سازی
        self.sync_enabled = False

        # تنظیمات نوار اسکرول
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setMinimumSize(400, 400)

        # فعال کردن mouse tracking
        self.setMouseTracking(True)
        self.image_label.setMouseTracking(True)

        # اتصال scroll bar ها برای emit کردن pan_changed
        self.horizontalScrollBar().valueChanged.connect(self._on_scroll_changed)
        self.verticalScrollBar().valueChanged.connect(self._on_scroll_changed)

    def _on_scroll_changed(self):
        """وقتی scroll position تغییر می‌کند"""
        if (
            not self.is_panning and self.sync_enabled
        ):  # فقط وقتی که sync فعال است و در حال pan نیست
            h = self.horizontalScrollBar().value()
            v = self.verticalScrollBar().value()
            self.pan_changed.emit(h, v)

    def set_crosshair(self, x: int, y: int):
        """نمایش crosshair در مختصات مشخص"""
        self.image_label.set_crosshair(x, y)

    def clear_crosshair(self):
        """حذف crosshair"""
        self.image_label.clear_crosshair()

    def set_image(self, image_array: np.ndarray):
        """تنظیم تصویر

        Args:
            image_array: آرایه numpy تصویر (grayscale یا RGB)
        """
        if image_array is None or image_array.size == 0:
            return

        try:
            # ذخیره ابعاد اصلی تصویر
            self.original_image_size = (
                image_array.shape[1],
                image_array.shape[0],
            )  # (width, height)

            # تبدیل numpy array به QImage
            if len(image_array.shape) == 2:  # Grayscale
                height, width = image_array.shape
                bytes_per_line = width
                q_image = QImage(
                    image_array.data,
                    width,
                    height,
                    bytes_per_line,
                    QImage.Format_Grayscale8,
                )
            else:  # RGB
                height, width, channels = image_array.shape
                bytes_per_line = channels * width
                q_image = QImage(
                    image_array.data,
                    width,
                    height,
                    bytes_per_line,
                    QImage.Format_RGB888,
                )

            # تبدیل به pixmap و ذخیره
            self.original_pixmap = QPixmap.fromImage(q_image)
            self.update_display()

        except Exception as e:
            print(f"Error in set_image: {e}")

    def update_display(self):
        """به‌روزرسانی نمایش با zoom فعلی"""
        if self.original_pixmap:
            scaled_pixmap = self.original_pixmap.scaled(
                self.original_pixmap.size() * self.zoom_factor,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            self.image_label.setPixmap(scaled_pixmap)
            self.image_label.resize(scaled_pixmap.size())
            self.image_label.zoom_factor = self.zoom_factor

    def set_zoom(self, zoom_factor: float):
        """تنظیم zoom از خارج (برای همگام‌سازی)"""
        self.zoom_factor = max(0.1, min(10.0, zoom_factor))
        self.update_display()

    def set_scroll_position(self, h: int, v: int):
        """تنظیم scroll position از خارج (برای همگام‌سازی)"""
        self.horizontalScrollBar().setValue(h)
        self.verticalScrollBar().setValue(v)

    def wheelEvent(self, event):
        """رویداد چرخ موس برای zoom"""
        if self.original_pixmap:
            # محاسبه مرکز zoom
            old_pos = self.mapFromGlobal(QCursor.pos())

            # تغییر zoom
            if event.angleDelta().y() > 0:
                self.zoom_factor *= config.ZOOM_WHEEL_FACTOR
            else:
                self.zoom_factor /= config.ZOOM_WHEEL_FACTOR

            # محدود کردن zoom
            self.zoom_factor = max(0.1, min(10.0, self.zoom_factor))

            self.update_display()

            # ارسال سیگنال zoom تغییر کرد
            if self.sync_enabled:
                self.zoom_changed.emit(self.zoom_factor)

            # تنظیم scroll برای حفظ نقطه زیر موس
            new_pos = self.mapFromGlobal(QCursor.pos())
            delta = new_pos - old_pos
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x()
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y()
            )

    def mousePressEvent(self, event: QMouseEvent):
        """شروع pan"""
        if event.button() == Qt.LeftButton and self.original_pixmap:
            self.is_panning = True
            self.pan_start_pos = event.pos()
            self.setCursor(Qt.ClosedHandCursor)

    def mouseMoveEvent(self, event: QMouseEvent):
        """حرکت موس - pan و ارسال مختصات"""
        if self.is_panning:
            # Pan
            delta = event.pos() - self.pan_start_pos
            self.pan_start_pos = event.pos()

            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x()
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y()
            )

            # ارسال سیگنال pan برای همگام‌سازی
            if self.sync_enabled:
                h = self.horizontalScrollBar().value()
                v = self.verticalScrollBar().value()
                self.pan_changed.emit(h, v)

        # محاسبه و ارسال مختصات در تصویر اصلی
        if self.original_pixmap and self.original_image_size:
            # موقعیت موس نسبت به image_label
            label_pos = self.image_label.mapFromGlobal(event.globalPosition().toPoint())

            # محاسبه مختصات در تصویر اصلی (با در نظر گرفتن zoom)
            if self.zoom_factor > 0:
                x = int(label_pos.x() / self.zoom_factor)
                y = int(label_pos.y() / self.zoom_factor)

                # بررسی محدوده
                if (
                    0 <= x < self.original_image_size[0]
                    and 0 <= y < self.original_image_size[1]
                ):
                    self.mouse_moved.emit(x, y)
                else:
                    self.mouse_moved.emit(-1, -1)  # خارج از تصویر
            else:
                self.mouse_moved.emit(-1, -1)
        else:
            self.mouse_moved.emit(-1, -1)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """پایان pan"""
        if event.button() == Qt.LeftButton:
            self.is_panning = False
            self.setCursor(
                Qt.OpenHandCursor if self.original_pixmap else Qt.ArrowCursor
            )

    def leaveEvent(self, event):
        """موس از viewer خارج شد"""
        # پاک کردن مختصات و ارسال سیگنال
        self.mouse_moved.emit(-1, -1)
        self.mouse_left.emit()
        super().leaveEvent(event)

    def zoom_in(self):
        """بزرگ‌نمایی"""
        if self.original_pixmap:
            self.zoom_factor *= 1.2
            self.zoom_factor = min(10.0, self.zoom_factor)
            self.update_display()
            if self.sync_enabled:
                self.zoom_changed.emit(self.zoom_factor)

    def zoom_out(self):
        """کوچک‌نمایی"""
        if self.original_pixmap:
            self.zoom_factor /= 1.2
            self.zoom_factor = max(0.1, self.zoom_factor)
            self.update_display()
            if self.sync_enabled:
                self.zoom_changed.emit(self.zoom_factor)

    def reset_zoom(self):
        """بازنشانی zoom"""
        self.zoom_factor = 1.0
        self.update_display()
        if self.sync_enabled:
            self.zoom_changed.emit(self.zoom_factor)

    def fit_to_window(self):
        """تنظیم اندازه تصویر به اندازه پنجره"""
        if self.original_pixmap:
            viewport_size = self.viewport().size()
            pixmap_size = self.original_pixmap.size()

            zoom_x = viewport_size.width() / pixmap_size.width()
            zoom_y = viewport_size.height() / pixmap_size.height()

            self.zoom_factor = min(zoom_x, zoom_y) * 0.95
            self.update_display()
            if self.sync_enabled:
                self.zoom_changed.emit(self.zoom_factor)

    def clear(self):
        """پاک کردن تصویر"""
        self.image_label.clear()
        self.original_pixmap = None
        self.zoom_factor = 1.0
        self.original_image_size = None
        self.clear_crosshair()
