"""
فیلترهای لبه‌یابی
Edge Detection Filters
"""

import cv2
import numpy as np


class EdgeFilters:
    """کلاس فیلترهای لبه‌یابی"""

    @staticmethod
    def canny(image: np.ndarray, **params) -> np.ndarray:
        """لبه‌یابی Canny"""
        threshold1 = params.get("threshold1", 100)
        threshold2 = params.get("threshold2", 200)

        gray = (
            cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        )
        edges = cv2.Canny(gray, threshold1, threshold2)

        return (
            cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR) if len(image.shape) == 3 else edges
        )

    @staticmethod
    def sobel(image: np.ndarray, **params) -> np.ndarray:
        """لبه‌یابی Sobel"""
        gray = (
            cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        )

        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)

        sobel = np.sqrt(sobelx**2 + sobely**2)
        sobel = np.uint8(sobel / sobel.max() * 255)

        return (
            cv2.cvtColor(sobel, cv2.COLOR_GRAY2BGR) if len(image.shape) == 3 else sobel
        )

    @staticmethod
    def laplacian(image: np.ndarray, **params) -> np.ndarray:
        """لبه‌یابی Laplacian"""
        gray = (
            cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        )

        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        laplacian = np.uint8(np.absolute(laplacian))

        return (
            cv2.cvtColor(laplacian, cv2.COLOR_GRAY2BGR)
            if len(image.shape) == 3
            else laplacian
        )

    @staticmethod
    def scharr(image: np.ndarray, **params) -> np.ndarray:
        """لبه‌یابی Scharr - دقیق‌تر از Sobel"""
        gray = (
            cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        )

        scharrx = cv2.Scharr(gray, cv2.CV_64F, 1, 0)
        scharry = cv2.Scharr(gray, cv2.CV_64F, 0, 1)

        scharr = np.sqrt(scharrx**2 + scharry**2)
        scharr = np.uint8(scharr / scharr.max() * 255)

        return (
            cv2.cvtColor(scharr, cv2.COLOR_GRAY2BGR)
            if len(image.shape) == 3
            else scharr
        )


# نقشه فیلترها
FILTER_MAP = {
    "edge_canny": EdgeFilters.canny,
    "edge_sobel": EdgeFilters.sobel,
    "edge_laplacian": EdgeFilters.laplacian,
    "edge_scharr": EdgeFilters.scharr,
}
