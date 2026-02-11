"""
مدیریت تصاویر - با پشتیبانی Convolution
Image Manager - با فیلترهای کانوولوشنی
"""

import cv2
import os
import numpy as np
from typing import Optional
from pathlib import Path

# ایمپورت تمام فیلترها
from filters.base_filters import FILTER_MAP as BASE_FILTERS
from filters.edge_filters import FILTER_MAP as EDGE_FILTERS
from filters.photogrammetry import FILTER_MAP as PHOTO_FILTERS
from filters.creative_filters import FILTER_MAP as CREATIVE_FILTERS
from filters.color_filters import FILTER_MAP as COLOR_FILTERS
from filters.convolution_filters import FILTER_MAP as CONV_FILTERS
from filters.transformation_filters import FILTER_MAP as TRANSFORM_FILTERS
from filters.point_detection_filters import FILTER_MAP as POINT_DETECTION_FILTERS


class ImageManager:
    """مدیریت بارگذاری، ذخیره و پردازش تصاویر"""

    # ترکیب تمام فیلترها
    ALL_FILTERS = {
        **BASE_FILTERS,
        **EDGE_FILTERS,
        **PHOTO_FILTERS,
        **CREATIVE_FILTERS,
        **COLOR_FILTERS,
        **CONV_FILTERS,
        **TRANSFORM_FILTERS,
        **POINT_DETECTION_FILTERS,
    }

    @staticmethod
    def load_image(file_path: str) -> Optional[np.ndarray]:
        """بارگذاری تصویر از فایل"""
        try:
            image = cv2.imread(file_path)
            if image is None:
                raise ValueError(f"Cannot load image: {file_path}")
            return image
        except Exception as e:
            print(f"Error loading image: {e}")
            return None

    @staticmethod
    def save_image(file_path: str, image: np.ndarray, quality: int = 90) -> bool:
        """ذخیره تصویر در فایل (با پشتیبانی کیفیت برای JPEG/WEBP)"""
        try:
            ext = os.path.splitext(file_path)[1].lower()

            params = []
            # OpenCV quality params
            if ext in [".jpg", ".jpeg"]:
                params = [int(cv2.IMWRITE_JPEG_QUALITY), int(max(0, min(100, quality)))]
            elif ext == ".webp":
                params = [int(cv2.IMWRITE_WEBP_QUALITY), int(max(0, min(100, quality)))]
            elif ext == ".png":
                # quality 0..100 -> compression 0..9 (inverse)
                comp = int(round(9 - (max(0, min(100, quality)) / 100.0) * 9))
                comp = max(0, min(9, comp))
                params = [int(cv2.IMWRITE_PNG_COMPRESSION), comp]

            success = cv2.imwrite(file_path, image, params) if params else cv2.imwrite(file_path, image)
            return bool(success)
        except Exception as e:
            print(f"Error saving image: {e}")
            return False

    @staticmethod
    def apply_filter(image: np.ndarray, filter_name: str, **params) -> np.ndarray:
        """اعمال فیلتر به تصویر"""
        if image is None or image.size == 0:
            return image

        try:
            # پیدا کردن و اجرای فیلتر
            if filter_name in ImageManager.ALL_FILTERS:
                filter_func = ImageManager.ALL_FILTERS[filter_name]
                return filter_func(image, **params)
            else:
                print(f"Filter not found: {filter_name}")
                return image.copy()
        except Exception as e:
            print(f"Error applying filter {filter_name}: {e}")
            return image.copy()

    @staticmethod
    def get_filter_list() -> dict:
        """دریافت لیست تمام فیلترها به تفکیک دسته"""
        return {
            "basic": list(BASE_FILTERS.keys()),
            "edge": list(EDGE_FILTERS.keys()),
            "photo": list(PHOTO_FILTERS.keys()),
            "creative": list(CREATIVE_FILTERS.keys()),
            "color": list(COLOR_FILTERS.keys()),
            "convolution": list(CONV_FILTERS.keys()),
            "transformation": list(TRANSFORM_FILTERS.keys()),
            "point_detection": list(POINT_DETECTION_FILTERS.keys()),
        }

    @staticmethod
    def validate_image(image: np.ndarray) -> bool:
        """اعتبارسنجی تصویر"""
        if image is None:
            return False
        if image.size == 0:
            return False
        if len(image.shape) not in [2, 3]:
            return False
        return True

    @staticmethod
    def get_image_info(image: np.ndarray) -> dict:
        """دریافت اطلاعات تصویر"""
        if not ImageManager.validate_image(image):
            return {}

        info = {
            "shape": image.shape,
            "dtype": str(image.dtype),
            "size": image.size,
        }

        if len(image.shape) == 3:
            info["channels"] = image.shape[2]
            info["width"] = image.shape[1]
            info["height"] = image.shape[0]
        else:
            info["channels"] = 1
            info["width"] = image.shape[1]
            info["height"] = image.shape[0]

        return info
