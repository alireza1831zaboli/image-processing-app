"""
Thread پردازش تصویر
Processing Thread
"""

import numpy as np
from PySide6.QtCore import QThread, Signal
from core.image_manager import ImageManager


class ProcessingThread(QThread):
    """ترد جداگانه برای پردازش تصاویر بدون فریز UI"""

    finished = Signal(np.ndarray)  # سیگنال اتمام با نتیجه
    error = Signal(str)  # سیگنال خطا
    progress = Signal(int)  # سیگنال پیشرفت (اختیاری)

    def __init__(self, image: np.ndarray, filter_name: str, params: dict):
        super().__init__()
        self.image = image.copy() if image is not None else None
        self.filter_name = filter_name
        self.params = params
        self._is_running = True

    def run(self):
        """اجرای پردازش"""
        try:
            if self.image is None:
                self.error.emit("تصویر معتبر نیست")
                return

            # اعمال فیلتر
            result = ImageManager.apply_filter(
                self.image, self.filter_name, **self.params
            )

            if self._is_running:
                self.finished.emit(result)

        except Exception as e:
            if self._is_running:
                self.error.emit(str(e))

    def stop(self):
        """توقف پردازش"""
        self._is_running = False
        self.quit()
