"""
نمایش‌گر هیستوگرام با Zoom، Pan و همگام‌سازی
Synced Zoomable Histogram Viewer
"""

import numpy as np
import cv2
from PySide6.QtWidgets import QScrollArea, QLabel
from PySide6.QtCore import Qt, QPoint, QSize, Signal
from PySide6.QtGui import QImage, QPixmap, QPainter, QColor, QFont, QCursor
import config


class SyncedHistogramViewer(QScrollArea):
    """ویجت نمایش هیستوگرام با zoom، pan و همگام‌سازی"""

    # سیگنال‌ها برای همگام‌سازی
    zoom_changed = Signal(float)  # zoom factor تغییر کرد
    pan_changed = Signal(int, int)  # scroll position تغییر کرد

    def __init__(self):
        super().__init__()

        # Label برای نمایش هیستوگرام
        self.histogram_label = QLabel()
        self.histogram_label.setAlignment(Qt.AlignCenter)
        self.histogram_label.setStyleSheet(
            f"""
            QLabel {{
                background-color: {config.Colors.IMAGE_VIEWER_BG};
                border: 2px solid {config.Colors.IMAGE_VIEWER_BORDER};
                border-radius: 8px;
            }}
            """
        )

        self.setWidget(self.histogram_label)
        self.setWidgetResizable(False)
        self.setAlignment(Qt.AlignCenter)

        # متغیرهای zoom و pan
        self.zoom_factor = 1.0
        self.original_pixmap = None
        self.is_panning = False
        self.pan_start_pos = QPoint()

        # برای همگام‌سازی
        self.sync_enabled = False

        # تنظیمات نوار اسکرول
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # سایز حداقل و پیشفرض
        self.setMinimumSize(400, 300)

        self.current_image = None

        # اتصال scroll bar ها برای emit کردن pan_changed
        self.horizontalScrollBar().valueChanged.connect(self._on_scroll_changed)
        self.verticalScrollBar().valueChanged.connect(self._on_scroll_changed)

    def _on_scroll_changed(self):
        """وقتی scroll position تغییر می‌کند"""
        if not self.is_panning and self.sync_enabled:
            h = self.horizontalScrollBar().value()
            v = self.verticalScrollBar().value()
            self.pan_changed.emit(h, v)

    def set_image(self, image_array: np.ndarray):
        """محاسبه و نمایش هیستوگرام تصویر"""
        if image_array is None or image_array.size == 0:
            return

        self.current_image = image_array
        self.calculate_and_draw_histogram()

    def calculate_and_draw_histogram(self):
        """محاسبه و رسم هیستوگرام"""
        if self.current_image is None:
            return

        # ابعاد canvas - ثابت برای کیفیت بهتر
        width = 1000
        height = 500

        # ایجاد تصویر با پس‌زمینه تیره
        canvas = np.ones((height, width, 3), dtype=np.uint8) * 40

        # محاسبه هیستوگرام
        if len(self.current_image.shape) == 2:  # Grayscale
            hist = cv2.calcHist([self.current_image], [0], None, [256], [0, 256])
            hist = hist.flatten()

            # نرمال‌سازی
            max_val = hist.max()
            if max_val > 0:
                hist_normalized = hist / max_val * (height - 100)
            else:
                hist_normalized = hist

            # رسم هیستوگرام
            bin_width = width // 256
            for i in range(256):
                h = int(hist_normalized[i])
                if h > 0:
                    x1 = i * bin_width
                    x2 = (i + 1) * bin_width
                    y1 = height - 50
                    y2 = height - 50 - h
                    cv2.rectangle(canvas, (x1, y2), (x2, y1), (200, 200, 200), -1)

            title = "Grayscale Histogram"

        else:  # RGB
            colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]  # BGR

            for i, color in enumerate(colors):
                hist = cv2.calcHist([self.current_image], [i], None, [256], [0, 256])
                hist = hist.flatten()

                # نرمال‌سازی
                max_val = hist.max()
                if max_val > 0:
                    hist_normalized = hist / max_val * (height - 100)
                else:
                    hist_normalized = hist

                # رسم خطوط
                bin_width = width // 256
                points = []
                for j in range(256):
                    h = int(hist_normalized[j])
                    x = j * bin_width + bin_width // 2
                    y = height - 50 - h
                    points.append((x, y))

                # رسم خط
                for j in range(len(points) - 1):
                    cv2.line(canvas, points[j], points[j + 1], color, 2)

            title = "RGB Histogram"

        # تبدیل به QPixmap
        h, w, ch = canvas.shape
        bytes_per_line = ch * w
        q_image = QImage(canvas.data, w, h, bytes_per_line, QImage.Format_RGB888)
        q_image = q_image.rgbSwapped()  # BGR to RGB

        pixmap = QPixmap.fromImage(q_image)

        # رسم متن روی pixmap
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # عنوان
        font = QFont("Arial", 16, QFont.Bold)
        painter.setFont(font)
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(15, 30, title)

        # محورها
        font_small = QFont("Arial", 11)
        painter.setFont(font_small)

        # محور X
        painter.drawText(width // 2 - 60, height - 15, "Pixel Intensity")
        painter.drawText(15, height - 15, "0")
        painter.drawText(width - 40, height - 15, "255")

        # محور Y
        painter.save()
        painter.translate(20, height // 2)
        painter.rotate(-90)
        painter.drawText(0, 0, "Frequency")
        painter.restore()

        # Legend برای RGB
        if len(self.current_image.shape) == 3:
            legend_x = width - 140
            legend_y = 60
            colors_rgb = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
            for i, (label, color) in enumerate(
                zip(["Red", "Green", "Blue"], colors_rgb)
            ):
                y = legend_y + i * 28
                # مربع رنگی
                painter.fillRect(legend_x, y - 12, 18, 18, QColor(*color))
                # متن
                painter.setPen(QColor(255, 255, 255))
                font_legend = QFont("Arial", 12)
                painter.setFont(font_legend)
                painter.drawText(legend_x + 25, y, label)

        painter.end()

        # ذخیره pixmap اصلی
        self.original_pixmap = pixmap
        self.zoom_factor = 1.0  # reset zoom
        self.update_display()

    def update_display(self):
        """به‌روزرسانی نمایش با zoom فعلی"""
        if self.original_pixmap:
            scaled_pixmap = self.original_pixmap.scaled(
                self.original_pixmap.size() * self.zoom_factor,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            self.histogram_label.setPixmap(scaled_pixmap)
            self.histogram_label.resize(scaled_pixmap.size())

    def set_zoom(self, zoom_factor: float):
        """تنظیم zoom از خارج (برای همگام‌سازی)"""
        self.zoom_factor = max(0.5, min(5.0, zoom_factor))
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
            self.zoom_factor = max(0.5, min(5.0, self.zoom_factor))

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

    def mousePressEvent(self, event):
        """شروع pan"""
        if event.button() == Qt.LeftButton and self.original_pixmap:
            self.is_panning = True
            self.pan_start_pos = event.pos()
            self.setCursor(Qt.ClosedHandCursor)

    def mouseMoveEvent(self, event):
        """حرکت موس - pan"""
        if self.is_panning:
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

    def mouseReleaseEvent(self, event):
        """پایان pan"""
        if event.button() == Qt.LeftButton:
            self.is_panning = False
            self.setCursor(
                Qt.OpenHandCursor if self.original_pixmap else Qt.ArrowCursor
            )

    def zoom_in(self):
        """بزرگ‌نمایی"""
        if self.original_pixmap:
            self.zoom_factor *= 1.2
            self.zoom_factor = min(5.0, self.zoom_factor)
            self.update_display()
            if self.sync_enabled:
                self.zoom_changed.emit(self.zoom_factor)

    def zoom_out(self):
        """کوچک‌نمایی"""
        if self.original_pixmap:
            self.zoom_factor /= 1.2
            self.zoom_factor = max(0.5, self.zoom_factor)
            self.update_display()
            if self.sync_enabled:
                self.zoom_changed.emit(self.zoom_factor)

    def reset_zoom(self):
        """بازنشانی zoom"""
        self.zoom_factor = 1.0
        self.update_display()
        if self.sync_enabled:
            self.zoom_changed.emit(self.zoom_factor)

    def clear(self):
        """پاک کردن هیستوگرام"""
        self.histogram_label.clear()
        self.current_image = None
        self.original_pixmap = None
        self.zoom_factor = 1.0

    def sizeHint(self):
        """پیشنهاد سایز - برای سایز اولیه"""
        return QSize(600, 350)

    def minimumSizeHint(self):
        """حداقل سایز"""
        return QSize(400, 300)
