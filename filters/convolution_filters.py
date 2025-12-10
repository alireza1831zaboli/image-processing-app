"""
فیلترهای کانوولوشنی - پیاده‌سازی دستی
Convolution Filters - Manual Implementation (No OpenCV filter2D)
"""

import numpy as np
from typing import Tuple


class ConvolutionFilters:
    """کلاس فیلترهای کانوولوشنی با پیاده‌سازی دستی"""

    # ========== Kernels آماده ==========

    KERNELS = {
        # Edge Detection
        "sobel_x": np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float32),
        "sobel_y": np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=np.float32),
        "prewitt_x": np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]], dtype=np.float32),
        "prewitt_y": np.array([[-1, -1, -1], [0, 0, 0], [1, 1, 1]], dtype=np.float32),
        "laplacian": np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]], dtype=np.float32),
        "laplacian_diag": np.array(
            [[1, 1, 1], [1, -8, 1], [1, 1, 1]], dtype=np.float32
        ),
        # Sharpen
        "sharpen_basic": np.array(
            [[0, -1, 0], [-1, 5, -1], [0, -1, 0]], dtype=np.float32
        ),
        "sharpen_strong": np.array(
            [[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]], dtype=np.float32
        ),
        "unsharp_mask": np.array(
            [[0, -1, 0], [-1, 5, -1], [0, -1, 0]], dtype=np.float32
        ),
        # Blur
        "box_blur": np.ones((3, 3), dtype=np.float32) / 9.0,
        "gaussian_approx": np.array([[1, 2, 1], [2, 4, 2], [1, 2, 1]], dtype=np.float32)
        / 16.0,
        # Emboss
        "emboss": np.array([[-2, -1, 0], [-1, 1, 1], [0, 1, 2]], dtype=np.float32),
        "emboss_subtle": np.array([[-1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=np.float32),
        # Edge Enhancement
        "edge_enhance": np.array([[0, 0, 0], [-1, 1, 0], [0, 0, 0]], dtype=np.float32),
        "outline": np.array(
            [[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]], dtype=np.float32
        ),
        # Identity
        "identity": np.array([[0, 0, 0], [0, 1, 0], [0, 0, 0]], dtype=np.float32),
    }

    # ========== Padding دستی ==========

    @staticmethod
    def apply_padding(
        image: np.ndarray, pad_size: int, padding_type: str = "replicate"
    ) -> np.ndarray:
        """
        اعمال padding به تصویر - کاملاً دستی

        Args:
            image: تصویر ورودی (2D برای grayscale یا 3D برای color)
            pad_size: اندازه padding
            padding_type: نوع padding
        """
        if padding_type == "none":
            return image

        if len(image.shape) == 2:
            # Grayscale
            h, w = image.shape
            padded = np.zeros((h + 2 * pad_size, w + 2 * pad_size), dtype=image.dtype)

            # کپی تصویر اصلی در مرکز
            padded[pad_size : h + pad_size, pad_size : w + pad_size] = image

            if padding_type == "zero":
                # قبلاً صفر هست، کاری نداره
                pass

            elif padding_type == "replicate":
                # تکرار لبه‌ها
                # بالا
                padded[:pad_size, pad_size : w + pad_size] = image[0:1, :]
                # پایین
                padded[h + pad_size :, pad_size : w + pad_size] = image[-1:, :]
                # چپ
                padded[pad_size : h + pad_size, :pad_size] = image[:, 0:1]
                # راست
                padded[pad_size : h + pad_size, w + pad_size :] = image[:, -1:]
                # گوشه‌ها
                padded[:pad_size, :pad_size] = image[0, 0]
                padded[:pad_size, w + pad_size :] = image[0, -1]
                padded[h + pad_size :, :pad_size] = image[-1, 0]
                padded[h + pad_size :, w + pad_size :] = image[-1, -1]

            elif padding_type == "reflect":
                # آینه‌ای (mirror)
                # بالا
                padded[:pad_size, pad_size : w + pad_size] = np.flip(
                    image[:pad_size, :], axis=0
                )
                # پایین
                padded[h + pad_size :, pad_size : w + pad_size] = np.flip(
                    image[-pad_size:, :], axis=0
                )
                # چپ
                padded[pad_size : h + pad_size, :pad_size] = np.flip(
                    image[:, :pad_size], axis=1
                )
                # راست
                padded[pad_size : h + pad_size, w + pad_size :] = np.flip(
                    image[:, -pad_size:], axis=1
                )
                # گوشه‌ها
                padded[:pad_size, :pad_size] = np.flip(
                    np.flip(image[:pad_size, :pad_size], axis=0), axis=1
                )
                padded[:pad_size, w + pad_size :] = np.flip(
                    np.flip(image[:pad_size, -pad_size:], axis=0), axis=1
                )
                padded[h + pad_size :, :pad_size] = np.flip(
                    np.flip(image[-pad_size:, :pad_size], axis=0), axis=1
                )
                padded[h + pad_size :, w + pad_size :] = np.flip(
                    np.flip(image[-pad_size:, -pad_size:], axis=0), axis=1
                )

            elif padding_type == "wrap":
                # دورانی (circular)
                # بالا
                padded[:pad_size, pad_size : w + pad_size] = image[-pad_size:, :]
                # پایین
                padded[h + pad_size :, pad_size : w + pad_size] = image[:pad_size, :]
                # چپ
                padded[pad_size : h + pad_size, :pad_size] = image[:, -pad_size:]
                # راست
                padded[pad_size : h + pad_size, w + pad_size :] = image[:, :pad_size]
                # گوشه‌ها
                padded[:pad_size, :pad_size] = image[-pad_size:, -pad_size:]
                padded[:pad_size, w + pad_size :] = image[-pad_size:, :pad_size]
                padded[h + pad_size :, :pad_size] = image[:pad_size, -pad_size:]
                padded[h + pad_size :, w + pad_size :] = image[:pad_size, :pad_size]

            return padded

        else:
            # Color (RGB)
            h, w, c = image.shape
            padded = np.zeros(
                (h + 2 * pad_size, w + 2 * pad_size, c), dtype=image.dtype
            )

            # اعمال padding به هر کانال
            for i in range(c):
                padded[:, :, i] = ConvolutionFilters.apply_padding(
                    image[:, :, i], pad_size, padding_type
                )

            return padded

    # ========== Convolution دستی ==========

    @staticmethod
    def manual_convolve_2d(
        image: np.ndarray, kernel: np.ndarray, padding_type: str = "replicate"
    ) -> np.ndarray:
        """
        کانوولوشن 2D دستی - بدون استفاده از cv2.filter2D

        Args:
            image: تصویر ورودی (2D - grayscale)
            kernel: ماتریس kernel
            padding_type: نوع padding
        """
        kernel = np.ascontiguousarray(kernel, dtype=np.float32)
        kernel_h, kernel_w = kernel.shape

        # فرض: kernel فرد است (3x3, 5x5, ...)
        pad_h = kernel_h // 2
        pad_w = kernel_w // 2

        # اعمال padding
        if padding_type != "none":
            padded = ConvolutionFilters.apply_padding(
                image, max(pad_h, pad_w), padding_type
            )
            output_h, output_w = image.shape
        else:
            padded = image
            output_h = image.shape[0] - kernel_h + 1
            output_w = image.shape[1] - kernel_w + 1

        # تصویر خروجی
        output = np.zeros((output_h, output_w), dtype=np.float32)

        # ✅ کانوولوشن با حلقه‌های تو در تو
        for i in range(output_h):
            for j in range(output_w):
                # استخراج region of interest
                region = padded[i : i + kernel_h, j : j + kernel_w].astype(np.float32)

                # ضرب element-wise و جمع
                output[i, j] = np.sum(region * kernel)

        return output

    @staticmethod
    def apply_kernel(
        image: np.ndarray,
        kernel: np.ndarray,
        normalize: bool = False,
        padding_type: str = "replicate",
    ) -> np.ndarray:
        """
        اعمال kernel به تصویر (با پیاده‌سازی دستی)

        Args:
            image: تصویر ورودی
            kernel: ماتریس kernel
            normalize: آیا نتیجه normalize شود؟
            padding_type: نوع padding
        """
        image = np.ascontiguousarray(image)
        kernel = np.ascontiguousarray(kernel, dtype=np.float32)

        if len(image.shape) == 3:
            # تصویر رنگی - اعمال به هر کانال
            result = np.zeros_like(image, dtype=np.float32)
            for i in range(image.shape[2]):
                result[:, :, i] = ConvolutionFilters.manual_convolve_2d(
                    image[:, :, i], kernel, padding_type
                )
        else:
            # تصویر خاکستری
            result = ConvolutionFilters.manual_convolve_2d(image, kernel, padding_type)

        # Normalize کردن اگر نیاز باشه
        if normalize:
            result_min = np.min(result)
            result_max = np.max(result)
            if result_max - result_min > 1e-6:
                result = 255.0 * (result - result_min) / (result_max - result_min)
            else:
                result = np.zeros_like(result)

        # Clip به 0-255
        result = np.clip(result, 0, 255).astype(np.uint8)

        return np.ascontiguousarray(result)

    # ========== متدهای فیلتر ==========

    @staticmethod
    def sobel_x(image: np.ndarray, **params) -> np.ndarray:
        """فیلتر Sobel X - لبه‌های عمودی"""
        kernel = ConvolutionFilters.KERNELS["sobel_x"]
        return ConvolutionFilters.apply_kernel(image, kernel, normalize=True)

    @staticmethod
    def sobel_y(image: np.ndarray, **params) -> np.ndarray:
        """فیلتر Sobel Y - لبه‌های افقی"""
        kernel = ConvolutionFilters.KERNELS["sobel_y"]
        return ConvolutionFilters.apply_kernel(image, kernel, normalize=True)

    @staticmethod
    def sobel_combined(image: np.ndarray, **params) -> np.ndarray:
        """ترکیب Sobel X و Y"""
        kernel_x = ConvolutionFilters.KERNELS["sobel_x"]
        kernel_y = ConvolutionFilters.KERNELS["sobel_y"]

        # محاسبه Sobel X و Y
        if len(image.shape) == 3:
            sobel_x = np.zeros_like(image, dtype=np.float32)
            sobel_y = np.zeros_like(image, dtype=np.float32)
            for i in range(image.shape[2]):
                sobel_x[:, :, i] = ConvolutionFilters.manual_convolve_2d(
                    image[:, :, i], kernel_x
                )
                sobel_y[:, :, i] = ConvolutionFilters.manual_convolve_2d(
                    image[:, :, i], kernel_y
                )
        else:
            sobel_x = ConvolutionFilters.manual_convolve_2d(image, kernel_x)
            sobel_y = ConvolutionFilters.manual_convolve_2d(image, kernel_y)

        # محاسبه magnitude
        magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
        magnitude = np.clip(magnitude, 0, 255).astype(np.uint8)

        return np.ascontiguousarray(magnitude)

    @staticmethod
    def prewitt_x(image: np.ndarray, **params) -> np.ndarray:
        """فیلتر Prewitt X"""
        kernel = ConvolutionFilters.KERNELS["prewitt_x"]
        return ConvolutionFilters.apply_kernel(image, kernel, normalize=True)

    @staticmethod
    def prewitt_y(image: np.ndarray, **params) -> np.ndarray:
        """فیلتر Prewitt Y"""
        kernel = ConvolutionFilters.KERNELS["prewitt_y"]
        return ConvolutionFilters.apply_kernel(image, kernel, normalize=True)

    @staticmethod
    def prewitt_combined(image: np.ndarray, **params) -> np.ndarray:
        """ترکیب Prewitt X و Y"""
        kernel_x = ConvolutionFilters.KERNELS["prewitt_x"]
        kernel_y = ConvolutionFilters.KERNELS["prewitt_y"]

        if len(image.shape) == 3:
            prewitt_x = np.zeros_like(image, dtype=np.float32)
            prewitt_y = np.zeros_like(image, dtype=np.float32)
            for i in range(image.shape[2]):
                prewitt_x[:, :, i] = ConvolutionFilters.manual_convolve_2d(
                    image[:, :, i], kernel_x
                )
                prewitt_y[:, :, i] = ConvolutionFilters.manual_convolve_2d(
                    image[:, :, i], kernel_y
                )
        else:
            prewitt_x = ConvolutionFilters.manual_convolve_2d(image, kernel_x)
            prewitt_y = ConvolutionFilters.manual_convolve_2d(image, kernel_y)

        magnitude = np.sqrt(prewitt_x**2 + prewitt_y**2)
        magnitude = np.clip(magnitude, 0, 255).astype(np.uint8)

        return np.ascontiguousarray(magnitude)

    @staticmethod
    def laplacian_filter(image: np.ndarray, **params) -> np.ndarray:
        """فیلتر Laplacian"""
        kernel = ConvolutionFilters.KERNELS["laplacian"]
        return ConvolutionFilters.apply_kernel(image, kernel, normalize=True)

    @staticmethod
    def laplacian_diagonal(image: np.ndarray, **params) -> np.ndarray:
        """فیلتر Laplacian با قطرها"""
        kernel = ConvolutionFilters.KERNELS["laplacian_diag"]
        return ConvolutionFilters.apply_kernel(image, kernel, normalize=True)

    @staticmethod
    def sharpen_basic(image: np.ndarray, **params) -> np.ndarray:
        """تیزکردن پایه"""
        kernel = ConvolutionFilters.KERNELS["sharpen_basic"]
        return ConvolutionFilters.apply_kernel(image, kernel)

    @staticmethod
    def sharpen_strong(image: np.ndarray, **params) -> np.ndarray:
        """تیزکردن قوی"""
        kernel = ConvolutionFilters.KERNELS["sharpen_strong"]
        return ConvolutionFilters.apply_kernel(image, kernel)

    @staticmethod
    def unsharp_mask(image: np.ndarray, **params) -> np.ndarray:
        """Unsharp Masking"""
        kernel = ConvolutionFilters.KERNELS["unsharp_mask"]
        return ConvolutionFilters.apply_kernel(image, kernel)

    @staticmethod
    def box_blur(image: np.ndarray, **params) -> np.ndarray:
        """Box Blur"""
        kernel = ConvolutionFilters.KERNELS["box_blur"]
        return ConvolutionFilters.apply_kernel(image, kernel)

    @staticmethod
    def gaussian_approx(image: np.ndarray, **params) -> np.ndarray:
        """تقریب Gaussian Blur"""
        kernel = ConvolutionFilters.KERNELS["gaussian_approx"]
        return ConvolutionFilters.apply_kernel(image, kernel)

    @staticmethod
    def emboss_filter(image: np.ndarray, **params) -> np.ndarray:
        """افکت Emboss"""
        kernel = ConvolutionFilters.KERNELS["emboss"]
        result = ConvolutionFilters.apply_kernel(image, kernel, normalize=False)
        result = np.clip(result.astype(np.int16) + 128, 0, 255).astype(np.uint8)
        return np.ascontiguousarray(result)

    @staticmethod
    def emboss_subtle(image: np.ndarray, **params) -> np.ndarray:
        """افکت Emboss ملایم"""
        kernel = ConvolutionFilters.KERNELS["emboss_subtle"]
        result = ConvolutionFilters.apply_kernel(image, kernel, normalize=False)
        result = np.clip(result.astype(np.int16) + 128, 0, 255).astype(np.uint8)
        return np.ascontiguousarray(result)

    @staticmethod
    def edge_enhance(image: np.ndarray, **params) -> np.ndarray:
        """تقویت لبه‌ها"""
        kernel = ConvolutionFilters.KERNELS["edge_enhance"]
        return ConvolutionFilters.apply_kernel(image, kernel, normalize=True)

    @staticmethod
    def outline(image: np.ndarray, **params) -> np.ndarray:
        """استخراج Outline"""
        kernel = ConvolutionFilters.KERNELS["outline"]
        return ConvolutionFilters.apply_kernel(image, kernel, normalize=True)

    @staticmethod
    def identity(image: np.ndarray, **params) -> np.ndarray:
        """Identity - بدون تغییر"""
        kernel = ConvolutionFilters.KERNELS["identity"]
        return ConvolutionFilters.apply_kernel(image, kernel)

    @staticmethod
    def custom_kernel(image: np.ndarray, **params) -> np.ndarray:
        """Custom Kernel - کاربر kernel خودش رو می‌ده"""
        kernel = params.get("kernel", None)
        normalize = params.get("normalize", False)
        padding = params.get("padding", "replicate")

        if kernel is None:
            kernel = ConvolutionFilters.KERNELS["identity"]

        kernel = np.ascontiguousarray(kernel, dtype=np.float32)

        print(
            f"🔍 Custom kernel shape: {kernel.shape}, normalize: {normalize}, padding: {padding}"
        )
        print(f"� Kernel:\n{kernel}")

        result = ConvolutionFilters.apply_kernel(image, kernel, normalize, padding)

        print(f"✅ Result shape: {result.shape}, dtype: {result.dtype}")

        return result


# ========== نقشه فیلترها ==========
FILTER_MAP = {
    "conv_sobel_x": ConvolutionFilters.sobel_x,
    "conv_sobel_y": ConvolutionFilters.sobel_y,
    "conv_sobel_combined": ConvolutionFilters.sobel_combined,
    "conv_prewitt_x": ConvolutionFilters.prewitt_x,
    "conv_prewitt_y": ConvolutionFilters.prewitt_y,
    "conv_prewitt_combined": ConvolutionFilters.prewitt_combined,
    "conv_laplacian": ConvolutionFilters.laplacian_filter,
    "conv_laplacian_diag": ConvolutionFilters.laplacian_diagonal,
    "conv_sharpen_basic": ConvolutionFilters.sharpen_basic,
    "conv_sharpen_strong": ConvolutionFilters.sharpen_strong,
    "conv_unsharp": ConvolutionFilters.unsharp_mask,
    "conv_box_blur": ConvolutionFilters.box_blur,
    "conv_gaussian": ConvolutionFilters.gaussian_approx,
    "conv_emboss": ConvolutionFilters.emboss_filter,
    "conv_emboss_subtle": ConvolutionFilters.emboss_subtle,
    "conv_edge_enhance": ConvolutionFilters.edge_enhance,
    "conv_outline": ConvolutionFilters.outline,
    "conv_identity": ConvolutionFilters.identity,
    "conv_custom": ConvolutionFilters.custom_kernel,
}
