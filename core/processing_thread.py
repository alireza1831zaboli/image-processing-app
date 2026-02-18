from PySide6.QtCore import QThread, Signal
from core.image_manager import ImageManager


class ProcessingThread(QThread):
    result = Signal(object)
    error = Signal(str)
    progress = Signal(int)

    def __init__(self, image, filter_name: str, params: dict):
        super().__init__()
        self.image = image.copy() if image is not None else None
        self.filter_name = filter_name
        self.params = params
        self._is_running = True

    def run(self):
        try:
            if self.image is None:
                self.error.emit("تصویر معتبر نیست")
                return

            result = ImageManager.apply_filter(
                self.image, self.filter_name, **self.params
            )

            if self._is_running:
                self.result.emit(result)

        except Exception as e:
            if self._is_running:
                self.error.emit(str(e))

    def stop(self):
        self._is_running = False
        self.quit()
