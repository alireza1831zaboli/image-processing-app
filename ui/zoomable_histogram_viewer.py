"""
نمایش‌گر هیستوگرام با قابلیت Zoom و Pan
Zoomable Histogram Viewer
"""

import numpy as np
import cv2
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea
from PySide6.QtCore import Qt, QPoint, QSize
from PySide6.QtGui import QImage, QPixmap, QPainter, QColor, QFont, QCursor
import config


class ZoomableHistogramViewer(QScrollArea):
    """ویجت نمایش هیستوگرام با zoom و pan"""

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

        # تنظیمات نوار اسکرول
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setMinimumSize(400, 300)

        self.current_image = None

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
        width = 1200
        height = 600

        # ایجاد تصویر با پس‌زمینه تیره
        canvas = np.ones((height, width, 3), dtype=np.uint8) * 40

        # محاسبه هیستوگرام
        if len(self.current_image.shape) == 2:  # Grayscale
            hist = cv2.calcHist([self.current_image], [0], None, [256], [0, 256])
            hist = hist.flatten()

            # نرمال‌سازی
            max_val = hist.max()
            if max_val > 0:
                hist_normalized = hist / max_val * (height - 120)
            else:
                hist_normalized = hist

            # رسم هیستوگرام
            bin_width = width // 256
            for i in range(256):
                h = int(hist_normalized[i])
                if h > 0:
                    x1 = i * bin_width
                    x2 = (i + 1) * bin_width
                    y1 = height - 60
                    y2 = height - 60 - h
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
                    hist_normalized = hist / max_val * (height - 120)
                else:
                    hist_normalized = hist

                # رسم خطوط
                bin_width = width // 256
                points = []
                for j in range(256):
                    h = int(hist_normalized[j])
                    x = j * bin_width + bin_width // 2
                    y = height - 60 - h
                    points.append((x, y))

                # رسم خط
                for j in range(len(points) - 1):
                    cv2.line(canvas, points[j], points[j + 1], color, 3)

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
        font = QFont("Arial", 18, QFont.Bold)
        painter.setFont(font)
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(20, 35, title)

        # محورها
        font_small = QFont("Arial", 12)
        painter.setFont(font_small)

        # محور X
        painter.drawText(width // 2 - 70, height - 20, "Pixel Intensity")
        painter.drawText(20, height - 20, "0")
        painter.drawText(width - 50, height - 20, "255")

        # محور Y
        painter.save()
        painter.translate(25, height // 2)
        painter.rotate(-90)
        painter.drawText(0, 0, "Frequency")
        painter.restore()

        # Legend برای RGB
        if len(self.current_image.shape) == 3:
            legend_x = width - 150
            legend_y = 70
            colors_rgb = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
            for i, (label, color) in enumerate(
                zip(["Red", "Green", "Blue"], colors_rgb)
            ):
                y = legend_y + i * 32
                # مربع رنگی
                painter.fillRect(legend_x, y - 14, 20, 20, QColor(*color))
                # متن
                painter.setPen(QColor(255, 255, 255))
                font_legend = QFont("Arial", 13)
                painter.setFont(font_legend)
                painter.drawText(legend_x + 28, y, label)

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

    def zoom_out(self):
        """کوچک‌نمایی"""
        if self.original_pixmap:
            self.zoom_factor /= 1.2
            self.zoom_factor = max(0.5, self.zoom_factor)
            self.update_display()

    def reset_zoom(self):
        """بازنشانی zoom"""
        self.zoom_factor = 1.0
        self.update_display()

    def clear(self):
        """پاک کردن هیستوگرام"""
        self.histogram_label.clear()
        self.current_image = None
        self.original_pixmap = None
        self.zoom_factor = 1.0

    def sizeHint(self):
        """پیشنهاد سایز"""
        return QSize(800, 400)

    def minimumSizeHint(self):
        """حداقل سایز"""
        return QSize(400, 300)
