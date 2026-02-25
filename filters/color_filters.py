import cv2
import numpy as np


class ColorFilters:

    @staticmethod
    def hsv(image: np.ndarray, **params) -> np.ndarray:
        return cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    @staticmethod
    def lab(image: np.ndarray, **params) -> np.ndarray:
        return cv2.cvtColor(image, cv2.COLOR_BGR2LAB)

    @staticmethod
    def hue_shift(image: np.ndarray, **params) -> np.ndarray:
        shift = params.get("shift", 30)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        hsv[:, :, 0] = (hsv[:, :, 0] + shift) % 180
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    @staticmethod
    def saturation_adjust(image: np.ndarray, **params) -> np.ndarray:
        factor = params.get("factor", 1.5)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * factor, 0, 255)
        return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

    @staticmethod
    def brightness_adjust(image: np.ndarray, **params) -> np.ndarray:
        value = params.get("value", 50)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 2] = np.clip(hsv[:, :, 2] + value, 0, 255)
        return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

    @staticmethod
    def temperature_adjust(image: np.ndarray, **params) -> np.ndarray:
        temp = params.get("temperature", 0)  # -100 تا 100

        if temp > 0:
            image = image.astype(np.float32)
            image[:, :, 2] = np.clip(image[:, :, 2] + temp, 0, 255)
            image[:, :, 0] = np.clip(image[:, :, 0] - temp * 0.5, 0, 255)
        else:
            image = image.astype(np.float32)
            image[:, :, 0] = np.clip(image[:, :, 0] - temp, 0, 255)
            image[:, :, 2] = np.clip(image[:, :, 2] + temp * 0.5, 0, 255)

        return image.astype(np.uint8)

    @staticmethod
    def invert_colors(image: np.ndarray, **params) -> np.ndarray:
        return 255 - image


FILTER_MAP = {
    "hsv": ColorFilters.hsv,
    "lab": ColorFilters.lab,
    "hue_shift": ColorFilters.hue_shift,
    "saturation_adjust": ColorFilters.saturation_adjust,
    "brightness_adjust": ColorFilters.brightness_adjust,
    "temperature_adjust": ColorFilters.temperature_adjust,
    "invert_colors": ColorFilters.invert_colors,
}
