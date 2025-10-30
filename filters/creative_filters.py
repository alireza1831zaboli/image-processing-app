"""
فیلترهای خلاقانه
Creative Filters
"""

import cv2
import numpy as np


class CreativeFilters:
    """کلاس فیلترهای خلاقانه"""

    @staticmethod
    def clay(image: np.ndarray, **params) -> np.ndarray:
        """افکت خاکی/گلی"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        edges_inv = cv2.bitwise_not(edges)
        clay = cv2.cvtColor(edges_inv, cv2.COLOR_GRAY2BGR)
        clay = cv2.GaussianBlur(clay, (3, 3), 0)

        # اضافه کردن رنگ گلی
        clay_colored = clay.copy()
        clay_colored[:, :, 0] = clay[:, :, 0] * 0.6  # کاهش آبی
        clay_colored[:, :, 1] = clay[:, :, 1] * 0.7  # کاهش سبز
        return clay_colored.astype(np.uint8)

    @staticmethod
    def negative(image: np.ndarray, **params) -> np.ndarray:
        """تصویر منفی"""
        return cv2.bitwise_not(image)

    @staticmethod
    def sepia(image: np.ndarray, **params) -> np.ndarray:
        """افکت سپیا - قدیمی"""
        kernel = np.array(
            [[0.272, 0.534, 0.131], [0.349, 0.686, 0.168], [0.393, 0.769, 0.189]]
        )
        sepia = cv2.transform(image, kernel)
        return np.clip(sepia, 0, 255).astype(np.uint8)

    @staticmethod
    def emboss(image: np.ndarray, **params) -> np.ndarray:
        """افکت برجسته"""
        kernel = np.array([[0, -1, -1], [1, 0, -1], [1, 1, 0]])
        embossed = cv2.filter2D(image, -1, kernel)
        embossed = cv2.add(embossed, 128)
        return embossed

    @staticmethod
    def cartoon(image: np.ndarray, **params) -> np.ndarray:
        """تبدیل به کارتون"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)
        edges = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9
        )
        color = cv2.bilateralFilter(image, 9, 300, 300)
        cartoon = cv2.bitwise_and(color, color, mask=edges)
        return cartoon

    @staticmethod
    def pencil_sketch(image: np.ndarray, **params) -> np.ndarray:
        """طراحی با مداد"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        inv_gray = cv2.bitwise_not(gray)
        blur = cv2.GaussianBlur(inv_gray, (21, 21), 0)
        sketch = cv2.divide(gray, cv2.bitwise_not(blur), scale=256.0)
        return cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)

    @staticmethod
    def oil_painting(image: np.ndarray, **params) -> np.ndarray:
        """افکت نقاشی رنگ روغن"""
        size = params.get("size", 7)
        dynRatio = params.get("dynRatio", 1)
        return cv2.xphoto.oilPainting(image, size, dynRatio)

    @staticmethod
    def watercolor(image: np.ndarray, **params) -> np.ndarray:
        """افکت آبرنگ"""
        # ترکیب bilateral filter و median blur
        result = cv2.bilateralFilter(image, 9, 75, 75)
        result = cv2.medianBlur(result, 5)
        return result


# نقشه فیلترها
FILTER_MAP = {
    "clay": CreativeFilters.clay,
    "negative": CreativeFilters.negative,
    "sepia": CreativeFilters.sepia,
    "emboss": CreativeFilters.emboss,
    "cartoon": CreativeFilters.cartoon,
    "pencil_sketch": CreativeFilters.pencil_sketch,
    "oil_painting": CreativeFilters.oil_painting,
    "watercolor": CreativeFilters.watercolor,
}
