"""
فیلترهای فوتوگرامتری
Photogrammetry Filters
"""

import cv2
import numpy as np


class PhotogrammetryFilters:
    """کلاس فیلترهای فوتوگرامتری"""

    @staticmethod
    def contrast_stretch(image: np.ndarray, **params) -> np.ndarray:
        """کشش کنتراست"""
        min_percentile = params.get("min_percentile", 2)
        max_percentile = params.get("max_percentile", 98)

        if len(image.shape) == 3:
            result = np.zeros_like(image)
            for i in range(3):
                p_low = np.percentile(image[:, :, i], min_percentile)
                p_high = np.percentile(image[:, :, i], max_percentile)
                result[:, :, i] = np.clip(
                    (image[:, :, i] - p_low) * 255.0 / (p_high - p_low), 0, 255
                )
            return result.astype(np.uint8)
        else:
            p_low = np.percentile(image, min_percentile)
            p_high = np.percentile(image, max_percentile)
            return np.clip((image - p_low) * 255.0 / (p_high - p_low), 0, 255).astype(
                np.uint8
            )

    @staticmethod
    def gamma_correction(image: np.ndarray, **params) -> np.ndarray:
        """تصحیح گاما"""
        gamma = params.get("gamma", 1.0)
        inv_gamma = 1.0 / gamma

        table = np.array(
            [((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]
        ).astype("uint8")

        return cv2.LUT(image, table)

    @staticmethod
    def threshold_binary(image: np.ndarray, **params) -> np.ndarray:
        """آستانه‌گذاری باینری"""
        threshold = params.get("threshold", 127)

        gray = (
            cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        )
        _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)

        return (
            cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
            if len(image.shape) == 3
            else binary
        )

    @staticmethod
    def threshold_otsu(image: np.ndarray, **params) -> np.ndarray:
        """آستانه‌گذاری Otsu - خودکار"""
        gray = (
            cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        )
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        return (
            cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
            if len(image.shape) == 3
            else binary
        )

    @staticmethod
    def adaptive_threshold(image: np.ndarray, **params) -> np.ndarray:
        """آستانه‌گذاری تطبیقی"""
        block_size = params.get("blockSize", 11)
        block_size = block_size if block_size % 2 == 1 else block_size + 1
        c = params.get("C", 2)

        gray = (
            cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        )
        adaptive = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_size, c
        )

        return (
            cv2.cvtColor(adaptive, cv2.COLOR_GRAY2BGR)
            if len(image.shape) == 3
            else adaptive
        )

    @staticmethod
    def morphology_erode(image: np.ndarray, **params) -> np.ndarray:
        """فرسایش مورفولوژیک"""
        kernel_size = params.get("kernel_size", 5)
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        return cv2.erode(image, kernel, iterations=1)

    @staticmethod
    def morphology_dilate(image: np.ndarray, **params) -> np.ndarray:
        """انبساط مورفولوژیک"""
        kernel_size = params.get("kernel_size", 5)
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        return cv2.dilate(image, kernel, iterations=1)

    @staticmethod
    def morphology_open(image: np.ndarray, **params) -> np.ndarray:
        """عملیات باز کردن مورفولوژیک"""
        kernel_size = params.get("kernel_size", 5)
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)

    @staticmethod
    def morphology_close(image: np.ndarray, **params) -> np.ndarray:
        """عملیات بستن مورفولوژیک"""
        kernel_size = params.get("kernel_size", 5)
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        return cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)


# نقشه فیلترها
FILTER_MAP = {
    "contrast_stretch": PhotogrammetryFilters.contrast_stretch,
    "gamma_correction": PhotogrammetryFilters.gamma_correction,
    "threshold_binary": PhotogrammetryFilters.threshold_binary,
    "threshold_otsu": PhotogrammetryFilters.threshold_otsu,
    "adaptive_threshold": PhotogrammetryFilters.adaptive_threshold,
    "morphology_erode": PhotogrammetryFilters.morphology_erode,
    "morphology_dilate": PhotogrammetryFilters.morphology_dilate,
    "morphology_open": PhotogrammetryFilters.morphology_open,
    "morphology_close": PhotogrammetryFilters.morphology_close,
}
