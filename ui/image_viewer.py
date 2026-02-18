import os
import numpy as np
from PySide6.QtWidgets import QLabel, QScrollArea, QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import Qt, QPoint, Signal
from PySide6.QtGui import QImage, QPixmap, QCursor, QMouseEvent, QPainter, QPen, QColor

import config


class ImageLabel(QLabel):

    def __init__(self):
        super().__init__()
        self.crosshair_pos = None
        self.zoom_factor = 1.0

    def set_crosshair(self, x: int, y: int):
        if x >= 0 and y >= 0:
            self.crosshair_pos = QPoint(x, y)
        else:
            self.crosshair_pos = None
        self.update()

    def clear_crosshair(self):
        self.crosshair_pos = None
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)

        if self.crosshair_pos and self.pixmap() and not self.pixmap().isNull():
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)

            x = int(self.crosshair_pos.x() * self.zoom_factor)
            y = int(self.crosshair_pos.y() * self.zoom_factor)

            pen = QPen(QColor(255, 0, 0, 200))
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawEllipse(QPoint(x, y), 8, 8)

            pen.setStyle(Qt.DashLine)
            painter.setPen(pen)
            painter.drawLine(x, 0, x, self.height())
            painter.drawLine(0, y, self.width(), y)

            painter.end()


class ImageViewer(QScrollArea):

    load_requested = Signal()
    file_dropped = Signal(str)

    mouse_moved = Signal(int, int)
    mouse_left = Signal()
    zoom_changed = Signal(float)
    pan_changed = Signal(int, int)

    def __init__(self):
        super().__init__()

        self.setAcceptDrops(True)

        self.image_label = ImageLabel()
        self.image_label.setAlignment(Qt.AlignCenter)

        self.setWidget(self.image_label)
        self.setWidgetResizable(False)
        self.setAlignment(Qt.AlignCenter)

        self.zoom_factor = 1.0
        self.original_pixmap = None
        self.original_image_size = None

        self._placeholder_text = "No image loaded"
        self._placeholder_subtext = ""
        self._has_image = False

        self._drag_active = False
        self._processing_active = False

        self.is_panning = False
        self.pan_start_pos = QPoint()

        self.sync_enabled = False

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setMinimumSize(400, 400)

        self.setMouseTracking(True)
        self.image_label.setMouseTracking(True)

        # --- Placeholder overlay ---
        self.placeholder_overlay = QWidget(self.viewport())
        self.placeholder_overlay.setObjectName("placeholderOverlay")
        self.placeholder_overlay.setAttribute(Qt.WA_TransparentForMouseEvents, False)

        ovl = QVBoxLayout(self.placeholder_overlay)
        ovl.setContentsMargins(24, 24, 24, 24)
        ovl.setSpacing(10)
        ovl.setAlignment(Qt.AlignCenter)

        self.placeholder_title = QLabel(self._placeholder_text)
        self.placeholder_title.setAlignment(Qt.AlignCenter)
        self.placeholder_title.setWordWrap(True)

        self.placeholder_subtitle = QLabel(self._placeholder_subtext)
        self.placeholder_subtitle.setAlignment(Qt.AlignCenter)
        self.placeholder_subtitle.setWordWrap(True)

        self.placeholder_button = QPushButton("📂 Load Image")
        self.placeholder_button.setProperty("variant", "primary")
        self.placeholder_button.setCursor(Qt.PointingHandCursor)
        self.placeholder_button.clicked.connect(self.load_requested.emit)

        ovl.addWidget(self.placeholder_title)
        ovl.addWidget(self.placeholder_subtitle)
        ovl.addWidget(self.placeholder_button)

        # --- Drag overlay ---
        self.drag_overlay = QWidget(self.viewport())
        self.drag_overlay.setObjectName("dragOverlay")
        self.drag_overlay.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        dvl = QVBoxLayout(self.drag_overlay)
        dvl.setContentsMargins(24, 24, 24, 24)
        dvl.setAlignment(Qt.AlignCenter)
        self.drag_label = QLabel("Drop to load image")
        self.drag_label.setAlignment(Qt.AlignCenter)
        self.drag_label.setWordWrap(True)
        dvl.addWidget(self.drag_label)

        # --- Processing overlay ---
        self.processing_overlay = QWidget(self.viewport())
        self.processing_overlay.setObjectName("processingOverlay")
        self.processing_overlay.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        pvl = QVBoxLayout(self.processing_overlay)
        pvl.setContentsMargins(24, 24, 24, 24)
        pvl.setSpacing(10)
        pvl.setAlignment(Qt.AlignCenter)

        self.processing_spinner = QLabel("⏳")
        self.processing_spinner.setAlignment(Qt.AlignCenter)

        self.processing_text = QLabel("Processing…")
        self.processing_text.setAlignment(Qt.AlignCenter)
        self.processing_text.setWordWrap(True)

        pvl.addWidget(self.processing_spinner)
        pvl.addWidget(self.processing_text)

        self.placeholder_overlay.hide()
        self.drag_overlay.hide()
        self.processing_overlay.hide()

        self._last_image_array = None

        self.horizontalScrollBar().valueChanged.connect(self._on_scroll_changed)
        self.verticalScrollBar().valueChanged.connect(self._on_scroll_changed)

        self.refresh_styles()
        self.show_placeholder()

    def refresh_styles(self):
        self.image_label.setStyleSheet(
            f"""
            QLabel {{
                background-color: {config.Colors.IMAGE_VIEWER_BG};
                border: 1px solid {config.Colors.IMAGE_VIEWER_BORDER};
                border-radius: 8px;
            }}
            """
        )

        self.placeholder_title.setStyleSheet(
            f"color: {config.Colors.TEXT}; font-size: {config.Fonts.SIZE_HEADER}px; font-weight: 700;"
        )
        self.placeholder_subtitle.setStyleSheet(
            f"color: {config.Colors.TEXT_SECONDARY}; font-size: {config.Fonts.SIZE_SMALL}px;"
        )

        self.drag_label.setStyleSheet(
            f"color: {config.Colors.TEXT}; font-size: {config.Fonts.SIZE_HEADER}px; font-weight: 600;"
        )
        self.drag_overlay.setStyleSheet(
            f"background: rgba(0,0,0,0.0); border: 2px dashed {config.Colors.PRIMARY}; border-radius: 10px;"
        )

        self.processing_spinner.setStyleSheet(
            f"color: {config.Colors.PRIMARY}; font-size: 28px; font-weight: 700; background: transparent;"
        )
        self.processing_text.setStyleSheet(
            f"color: {config.Colors.TEXT}; font-size: {config.Fonts.SIZE_BASE}px; background: transparent;"
        )
        self.processing_overlay.setStyleSheet(
            "background: rgba(0,0,0,0.25); border-radius: 10px;"
        )

        self.placeholder_button.setStyleSheet(
            f"""
            QPushButton[variant="primary"] {{
                background-color: {config.Colors.PRIMARY};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 14px;
                font-weight: 600;
            }}
            QPushButton[variant="primary"]:hover {{
                background-color: {config.Colors.PRIMARY_HOVER};
            }}
            QPushButton[variant="primary"]:pressed {{
                background-color: {config.Colors.PRIMARY_HOVER};
            }}
            """
        )

    def set_placeholder_text(self, title: str, subtitle: str = ""):
        self._placeholder_text = title or "No image loaded"
        self._placeholder_subtext = subtitle or ""
        self.placeholder_title.setText(self._placeholder_text)
        self.placeholder_subtitle.setText(self._placeholder_subtext)

    def show_placeholder(self):
        self._has_image = False
        self.image_label.clear()
        self.image_label.hide()
        self.original_pixmap = None
        self.original_image_size = None
        self.zoom_factor = 1.0
        self.clear_crosshair()
        self.hide_processing()

        self.placeholder_title.setText(self._placeholder_text)
        self.placeholder_subtitle.setText(self._placeholder_subtext)

        self.placeholder_overlay.setGeometry(self.viewport().rect())
        self.placeholder_overlay.show()
        self.placeholder_overlay.raise_()

    def show_processing(self, message: str = "Processing…"):
        self._processing_active = True
        self.processing_text.setText(message or "Processing…")
        self.processing_overlay.setGeometry(self.viewport().rect())
        self.processing_overlay.show()
        self.processing_overlay.raise_()

    def hide_processing(self):
        self._processing_active = False
        self.processing_overlay.hide()

    def _set_drag_active(self, active: bool):
        self._drag_active = active
        if active:
            self.drag_overlay.setGeometry(self.viewport().rect())
            self.drag_overlay.show()
            self.drag_overlay.raise_()
        else:
            self.drag_overlay.hide()

    def _on_scroll_changed(self):
        if not self.is_panning and self.sync_enabled:
            h = self.horizontalScrollBar().value()
            v = self.verticalScrollBar().value()
            self.pan_changed.emit(h, v)

    def set_crosshair(self, x: int, y: int):
        self.image_label.set_crosshair(x, y)

    def clear_crosshair(self):
        self.image_label.clear_crosshair()

    def set_image(self, image_array: np.ndarray):
        if image_array is None or image_array.size == 0:
            self.show_placeholder()
            return

        try:
            self.original_image_size = (image_array.shape[1], image_array.shape[0])

            if len(image_array.shape) == 2:
                height, width = image_array.shape
                bytes_per_line = width
                self._last_image_array = image_array
                q_image = QImage(
                    image_array.data,
                    width,
                    height,
                    bytes_per_line,
                    QImage.Format_Grayscale8,
                )
                q_image = q_image.copy()
            else:
                height, width, channels = image_array.shape
                image_array = np.ascontiguousarray(image_array)
                bytes_per_line = channels * width

                if hasattr(QImage, "Format_BGR888"):
                    self._last_image_array = image_array
                    q_image = QImage(
                        image_array.data,
                        width,
                        height,
                        bytes_per_line,
                        QImage.Format_BGR888,
                    )
                    q_image = q_image.copy()
                else:
                    rgb = np.ascontiguousarray(image_array[:, :, ::-1])
                    self._last_image_array = image_array
                    q_image = QImage(
                        rgb.data,
                        width,
                        height,
                        bytes_per_line,
                        QImage.Format_RGB888,
                    )
                    q_image = q_image.copy()

            self.original_pixmap = QPixmap.fromImage(q_image)
            self._has_image = True
            self.image_label.show()
            self.placeholder_overlay.hide()
            self.drag_overlay.hide()
            self.hide_processing()
            self.update_display()
        except Exception as e:
            print(f"Error in set_image: {e}")
            self.show_placeholder()

    def update_display(self):
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
        self.zoom_factor = max(0.1, min(10.0, zoom_factor))
        self.update_display()

    def set_scroll_position(self, h: int, v: int):
        self.horizontalScrollBar().setValue(h)
        self.verticalScrollBar().setValue(v)

    # --- Drag & Drop events ---
    def dragEnterEvent(self, event):
        md = event.mimeData()
        if md and md.hasUrls():
            url = md.urls()[0]
            if url.isLocalFile():
                p = url.toLocalFile()
                ext = os.path.splitext(p)[1].lower()
                if ext in [".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp"]:
                    event.acceptProposedAction()
                    self._set_drag_active(True)
                    return
        event.ignore()

    def dragMoveEvent(self, event):
        md = event.mimeData()
        if md and md.hasUrls():
            event.acceptProposedAction()
            return
        event.ignore()

    def dragLeaveEvent(self, event):
        self._set_drag_active(False)
        event.accept()

    def dropEvent(self, event):
        self._set_drag_active(False)
        md = event.mimeData()
        if md and md.hasUrls():
            url = md.urls()[0]
            if url.isLocalFile():
                p = url.toLocalFile()
                ext = os.path.splitext(p)[1].lower()
                if ext in [".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp"]:
                    self.file_dropped.emit(p)
                    event.acceptProposedAction()
                    return
        event.ignore()

    # --- Resize ---
    def resizeEvent(self, event):
        super().resizeEvent(event)
        r = self.viewport().rect()
        self.placeholder_overlay.setGeometry(r)
        self.drag_overlay.setGeometry(r)
        self.processing_overlay.setGeometry(r)

    # --- Zoom / Pan / Mouse tracking ---
    def wheelEvent(self, event):
        if self.original_pixmap and not self._processing_active:
            old_pos = self.mapFromGlobal(QCursor.pos())

            if event.angleDelta().y() > 0:
                self.zoom_factor *= config.ZOOM_WHEEL_FACTOR
            else:
                self.zoom_factor /= config.ZOOM_WHEEL_FACTOR

            self.zoom_factor = max(0.1, min(10.0, self.zoom_factor))
            self.update_display()

            if self.sync_enabled:
                self.zoom_changed.emit(self.zoom_factor)

            new_pos = self.mapFromGlobal(QCursor.pos())
            delta = new_pos - old_pos
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x()
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y()
            )

    def mousePressEvent(self, event: QMouseEvent):
        if (
            event.button() == Qt.LeftButton
            and self.original_pixmap
            and not self._processing_active
        ):
            self.is_panning = True
            self.pan_start_pos = event.pos()
            self.setCursor(Qt.ClosedHandCursor)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.is_panning:
            delta = event.pos() - self.pan_start_pos
            self.pan_start_pos = event.pos()

            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x()
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y()
            )

            if self.sync_enabled:
                h = self.horizontalScrollBar().value()
                v = self.verticalScrollBar().value()
                self.pan_changed.emit(h, v)

        if self.original_pixmap and self.original_image_size:
            label_pos = self.image_label.mapFromGlobal(event.globalPosition().toPoint())
            if self.zoom_factor > 0:
                x = int(label_pos.x() / self.zoom_factor)
                y = int(label_pos.y() / self.zoom_factor)

                if (
                    0 <= x < self.original_image_size[0]
                    and 0 <= y < self.original_image_size[1]
                ):
                    self.mouse_moved.emit(x, y)
                else:
                    self.mouse_moved.emit(-1, -1)
            else:
                self.mouse_moved.emit(-1, -1)
        else:
            self.mouse_moved.emit(-1, -1)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.is_panning = False
            self.setCursor(
                Qt.OpenHandCursor if self.original_pixmap else Qt.ArrowCursor
            )

    def leaveEvent(self, event):
        self.mouse_moved.emit(-1, -1)
        self.mouse_left.emit()
        super().leaveEvent(event)

    def zoom_in(self):
        if self.original_pixmap and not self._processing_active:
            self.zoom_factor *= 1.2
            self.zoom_factor = min(10.0, self.zoom_factor)
            self.update_display()
            if self.sync_enabled:
                self.zoom_changed.emit(self.zoom_factor)

    def zoom_out(self):
        if self.original_pixmap and not self._processing_active:
            self.zoom_factor /= 1.2
            self.zoom_factor = max(0.1, self.zoom_factor)
            self.update_display()
            if self.sync_enabled:
                self.zoom_changed.emit(self.zoom_factor)

    def reset_zoom(self):
        self.zoom_factor = 1.0
        self.update_display()
        if self.sync_enabled:
            self.zoom_changed.emit(self.zoom_factor)

    def fit_to_window(self):
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
        self._placeholder_text = "No image loaded"
        self._placeholder_subtext = ""
        self.show_placeholder()
