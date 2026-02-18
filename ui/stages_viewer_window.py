"""نمایش مراحل پردازش (Project windows)

Stages Viewer Window

این پنجره برای پروژه‌ها/فیلترهایی است که علاوه بر خروجی نهایی،
تصاویر مراحل میانی را هم تولید می‌کنند (مثل پروژه ۴ - Canny).
"""

from __future__ import annotations

from typing import List, Tuple

import numpy as np

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QGridLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


class StagesViewerWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🧩 مراحل پردازش")
        self.setModal(False)
        # اگر کاربر پنجره را ببندد، آبجکت هم حذف شود تا دفعه بعد clean ساخته شود.
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.resize(900, 700)

        self._root = QVBoxLayout(self)
        self._root.setContentsMargins(10, 10, 10, 10)
        self._root.setSpacing(8)

        header = QLabel("مراحل پردازش")
        header.setStyleSheet(
            "font-size: 14px; font-weight: 700; padding: 6px 2px;"
        )
        self._root.addWidget(header)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self._content = QWidget()
        self._grid = QGridLayout(self._content)
        self._grid.setContentsMargins(0, 0, 0, 0)
        self._grid.setHorizontalSpacing(14)
        self._grid.setVerticalSpacing(18)

        self._scroll.setWidget(self._content)
        self._root.addWidget(self._scroll, 1)

    def _clear_grid(self):
        while self._grid.count():
            item = self._grid.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

    def set_stages(self, stages: List[Tuple[str, np.ndarray]]):
        self._clear_grid()

        cols = 2
        max_w = 420
        max_h = 320

        for idx, (title, img) in enumerate(stages):
            r = idx // cols
            c = idx % cols

            title_lbl = QLabel(title)
            title_lbl.setWordWrap(True)
            title_lbl.setStyleSheet(
                "font-weight: 700; padding: 2px 2px;"
            )

            img_lbl = QLabel()
            img_lbl.setAlignment(Qt.AlignCenter)
            img_lbl.setStyleSheet(
                "background: rgba(0,0,0,0.05); border: 1px solid rgba(0,0,0,0.15); border-radius: 10px; padding: 6px;"
            )

            pix = self._to_pixmap(img)
            if not pix.isNull():
                pix = pix.scaled(max_w, max_h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                img_lbl.setPixmap(pix)
            else:
                img_lbl.setText("(تصویر نامعتبر)")

            cell = QWidget()
            v = QVBoxLayout(cell)
            v.setContentsMargins(0, 0, 0, 0)
            v.setSpacing(6)
            v.addWidget(title_lbl)
            v.addWidget(img_lbl)

            self._grid.addWidget(cell, r, c)

        self._grid.setRowStretch((len(stages) + 1) // cols, 1)

    def _to_pixmap(self, img: np.ndarray) -> QPixmap:
        if img is None or getattr(img, "size", 0) == 0:
            return QPixmap()

        try:
            if img.dtype != np.uint8:
                img = np.clip(img, 0, 255).astype(np.uint8)

            if len(img.shape) == 2:
                h, w = img.shape
                q = QImage(img.data, w, h, w, QImage.Format_Grayscale8).copy()
                return QPixmap.fromImage(q)

            h, w, ch = img.shape
            img = np.ascontiguousarray(img)
            bytes_per_line = ch * w

            if hasattr(QImage, "Format_BGR888"):
                q = QImage(img.data, w, h, bytes_per_line, QImage.Format_BGR888).copy()
                return QPixmap.fromImage(q)

            rgb = np.ascontiguousarray(img[:, :, ::-1])
            q = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888).copy()
            return QPixmap.fromImage(q)
        except Exception:
            return QPixmap()
