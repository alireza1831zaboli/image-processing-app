"""
فیلترهای پایه پردازش تصویر
Basic Image Processing Filters
"""

import cv2
import numpy as np
from typing import Optional


class BaseFilters:
    """کلاس فیلترهای پایه"""

    @staticmethod
    def original(image: np.ndarray, **params) -> np.ndarray:
        """برگرداندن تصویر اصلی بدون تغییر"""
        return image.copy()

    @staticmethod
    def grayscale(image: np.ndarray, **params) -> np.ndarray:
        """تبدیل به خاکستری"""
        if len(image.shape) == 2:
            return image
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    @staticmethod
    def blur(image: np.ndarray, **params) -> np.ndarray:
        """محو کردن گوسی"""
        ksize = params.get("ksize", 15)
        ksize = ksize if ksize % 2 == 1 else ksize + 1
        ksize = max(1, ksize)
        return cv2.GaussianBlur(image, (ksize, ksize), 0)

    @staticmethod
    def sharpen(image: np.ndarray, **params) -> np.ndarray:
        """تیز کردن تصویر"""
        kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        return cv2.filter2D(image, -1, kernel)

    @staticmethod
    def bilateral(image: np.ndarray, **params) -> np.ndarray:
        """فیلتر دو سویه - حفظ لبه‌ها"""
        d = params.get("d", 9)
        sigma_color = params.get("sigmaColor", 75)
        sigma_space = params.get("sigmaSpace", 75)
        return cv2.bilateralFilter(image, d, sigma_color, sigma_space)

    @staticmethod
    def median(image: np.ndarray, **params) -> np.ndarray:
        """فیلتر میانه - حذف نویز"""
        ksize = params.get("ksize", 5)
        ksize = ksize if ksize % 2 == 1 else ksize + 1
        ksize = max(1, min(31, ksize))
        return cv2.medianBlur(image, ksize)

    @staticmethod
    def histogram_equalization(image: np.ndarray, **params) -> np.ndarray:
        """همسان‌سازی هیستوگرام"""
        if len(image.shape) == 2:
            return cv2.equalizeHist(image)
        else:
            ycrcb = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
            ycrcb[:, :, 0] = cv2.equalizeHist(ycrcb[:, :, 0])
            return cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)

    @staticmethod
    def clahe(image: np.ndarray, **params) -> np.ndarray:
        """CLAHE - بهبود کنتراست محلی"""
        clip_limit = params.get("clipLimit", 2.0)
        tile_grid_size = params.get("tileGridSize", 8)

        clahe = cv2.createCLAHE(
            clipLimit=clip_limit, tileGridSize=(tile_grid_size, tile_grid_size)
        )

        if len(image.shape) == 2:
            return clahe.apply(image)
        else:
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            lab[:, :, 0] = clahe.apply(lab[:, :, 0])
            return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)


# نقشه فیلترها برای دسترسی آسان
FILTER_MAP = {
    "original": BaseFilters.original,
    "grayscale": BaseFilters.grayscale,
    "blur": BaseFilters.blur,
    "sharpen": BaseFilters.sharpen,
    "bilateral": BaseFilters.bilateral,
    "median": BaseFilters.median,
    "histogram_equalization": BaseFilters.histogram_equalization,
    "clahe": BaseFilters.clahe,
}
