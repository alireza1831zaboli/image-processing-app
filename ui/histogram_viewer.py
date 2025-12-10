"""
نمایش‌گر هیستوگرام
Histogram Viewer
"""

import numpy as np
import cv2
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QImage, QPixmap, QPainter, QPen, QColor, QFont
import config


class HistogramViewer(QWidget):
    """ویجت نمایش هیستوگرام تصویر"""

    def __init__(self):
        super().__init__()

        # تنظیم size policy
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.histogram_label = QLabel()
        self.histogram_label.setAlignment(Qt.AlignCenter)
        self.histogram_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.histogram_label.setScaledContents(False)  # مهم: جلوگیری از stretch
        self.histogram_label.setStyleSheet(
            f"""
            QLabel {{
                background-color: {config.Colors.IMAGE_VIEWER_BG};
                border: 2px solid {config.Colors.IMAGE_VIEWER_BORDER};
                border-radius: 8px;
            }}
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.addWidget(self.histogram_label)

        self.current_image = None
        self.original_pixmap = None

        # حداقل و حداکثر سایز
        self.setMinimumSize(400, 300)

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
        width = 900
        height = 450

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
            legend_x = width - 130
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
                painter.drawText(legend_x + 25, y, label)

        painter.end()

        # ذخیره pixmap اصلی
        self.original_pixmap = pixmap

        # نمایش با scale مناسب
        self.update_display()

    def update_display(self):
        """به‌روزرسانی نمایش با scale مناسب"""
        if not self.original_pixmap or self.original_pixmap.isNull():
            return

        # سایز label
        label_size = self.histogram_label.size()

        # scale کردن pixmap برای fit شدن در label
        if label_size.width() > 50 and label_size.height() > 50:
            scaled = self.original_pixmap.scaled(
                label_size, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.histogram_label.setPixmap(scaled)
        else:
            # اگر سایز خیلی کوچیک بود، از اصلی استفاده کن
            self.histogram_label.setPixmap(self.original_pixmap)

    def clear(self):
        """پاک کردن هیستوگرام"""
        self.histogram_label.clear()
        self.current_image = None
        self.original_pixmap = None

    def resizeEvent(self, event):
        """تنظیم اندازه هنگام resize"""
        super().resizeEvent(event)
        # فقط اگر pixmap موجود باشه update کن
        if self.original_pixmap and not self.original_pixmap.isNull():
            self.update_display()

    def sizeHint(self):
        """پیشنهاد سایز مناسب"""
        return QSize(800, 400)

    def minimumSizeHint(self):
        """حداقل سایز مناسب"""
        return QSize(400, 300)
