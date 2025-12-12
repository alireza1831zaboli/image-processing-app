import numpy as np
from typing import Optional, Tuple
from numba import jit, prange  # برای بهینه‌سازی سرعت


class ConvolutionFilters:
    # ========== Kernels ==========
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
        )
        / 1.0,
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

    @staticmethod
    def pad_image(image: np.ndarray, pad: int, mode: str = "replicate") -> np.ndarray:
        if pad == 0:
            return image

        h, w = image.shape[:2]
        is_color = len(image.shape) == 3

        if is_color:
            new_h, new_w, c = h + 2 * pad, w + 2 * pad, image.shape[2]
            padded = np.zeros((new_h, new_w, c), dtype=image.dtype)
        else:
            new_h, new_w = h + 2 * pad, w + 2 * pad
            padded = np.zeros((new_h, new_w), dtype=image.dtype)

        if is_color:
            padded[pad : pad + h, pad : pad + w, :] = image
        else:
            padded[pad : pad + h, pad : pad + w] = image

        if mode == "replicate":
            padded[:pad, pad : pad + w] = image[0:1, :]
            padded[pad + h :, pad : pad + w] = image[h - 1 : h, :]
            padded[pad : pad + h, :pad] = image[:, 0:1]
            padded[pad : pad + h, pad + w :] = image[:, w - 1 : w]

            padded[:pad, :pad] = image[0:1, 0:1]  # بالا-چپ
            padded[:pad, pad + w :] = image[0:1, w - 1 : w]  # بالا-راست
            padded[pad + h :, :pad] = image[h - 1 : h, 0:1]  # پایین-چپ
            padded[pad + h :, pad + w :] = image[h - 1 : h, w - 1 : w]  # پایین-راست

        elif mode == "reflect":
            for i in range(pad):
                padded[i, pad : pad + w] = image[pad - i - 1, :]
                padded[pad + h + i, pad : pad + w] = image[h - i - 1, :]
                padded[pad : pad + h, i] = image[:, pad - i - 1]
                padded[pad : pad + h, pad + w + i] = image[:, w - i - 1]

        elif mode == "wrap":
            for i in range(pad):
                padded[i, pad : pad + w] = image[h - pad + i, :]
                padded[pad + h + i, pad : pad + w] = image[i, :]
                padded[pad : pad + h, i] = image[:, w - pad + i]
                padded[pad : pad + h, pad + w + i] = image[:, i]

        return padded

    # ========== Convolution دستی بهینه شده ==========

    @staticmethod
    @jit(nopython=True, parallel=True, cache=True)
    def _convolve_2d_numba(image: np.ndarray, kernel: np.ndarray) -> np.ndarray:
        """
        Convolution 2D با Numba برای بهینه‌سازی سرعت
        برای تصاویر grayscale
        """
        h, w = image.shape
        kh, kw = kernel.shape
        pad_h = kh // 2
        pad_w = kw // 2

        result_h = h - 2 * pad_h
        result_w = w - 2 * pad_w
        result = np.zeros((result_h, result_w), dtype=np.float32)

        # Parallel loop با numba
        for i in prange(result_h):
            for j in range(result_w):
                value = 0.0
                for ki in range(kh):
                    for kj in range(kw):
                        value += image[i + ki, j + kj] * kernel[ki, kj]
                result[i, j] = value

        return result

    @staticmethod
    def convolve_manual(
        image: np.ndarray, kernel: np.ndarray, padding: str = "replicate"
    ) -> np.ndarray:
        """
        Convolution دستی کامل - بدون استفاده از توابع آماده

        Args:
            image: تصویر ورودی
            kernel: کرنل convolution
            padding: نوع padding

        Returns:
            تصویر پردازش شده
        """
        kh, kw = kernel.shape
        pad = kh // 2

        is_color = len(image.shape) == 3

        if padding == "none":
            # بدون padding - سایز کوچکتر میشه
            padded = image
        else:
            # با padding - سایز حفظ میشه
            padded = ConvolutionFilters.pad_image(image, pad, padding)

        if is_color:
            # پردازش هر کانال جداگانه
            h, w, c = image.shape

            if padding == "none":
                result_h, result_w = h - 2 * pad, w - 2 * pad
                result = np.zeros((result_h, result_w, c), dtype=np.float32)
            else:
                result = np.zeros((h, w, c), dtype=np.float32)

            for channel in range(c):
                try:
                    # استفاده از Numba برای سرعت
                    result[:, :, channel] = ConvolutionFilters._convolve_2d_numba(
                        padded[:, :, channel].astype(np.float32), kernel
                    )
                except:
                    # اگر Numba کار نکرد، روش معمولی
                    result[:, :, channel] = ConvolutionFilters._convolve_2d_manual(
                        padded[:, :, channel], kernel
                    )
        else:
            # Grayscale
            try:
                result = ConvolutionFilters._convolve_2d_numba(
                    padded.astype(np.float32), kernel
                )
            except:
                result = ConvolutionFilters._convolve_2d_manual(padded, kernel)

        return result

    @staticmethod
    def _convolve_2d_manual(image: np.ndarray, kernel: np.ndarray) -> np.ndarray:
        """
        Convolution 2D دستی بدون Numba (fallback)
        """
        h, w = image.shape
        kh, kw = kernel.shape
        pad_h = kh // 2
        pad_w = kw // 2

        result_h = h - 2 * pad_h
        result_w = w - 2 * pad_w
        result = np.zeros((result_h, result_w), dtype=np.float32)

        for i in range(result_h):
            for j in range(result_w):
                # استخراج پنجره
                window = image[i : i + kh, j : j + kw]
                # ضرب element-wise و جمع
                result[i, j] = np.sum(window * kernel)

        return result

    @staticmethod
    def apply_kernel(
        image: np.ndarray,
        kernel: np.ndarray,
        normalize: bool = False,
        padding_type: str = "replicate",
    ) -> np.ndarray:
        """
        اعمال kernel با convolution دستی

        Args:
            image: تصویر ورودی
            kernel: کرنل
            normalize: نرمالسازی خروجی
            padding_type: نوع padding

        Returns:
            تصویر پردازش شده
        """
        # Convolution دستی
        result = ConvolutionFilters.convolve_manual(image, kernel, padding_type)

        # Clip کردن مقادیر
        result = np.clip(result, 0, 255)

        # Normalize اگر نیاز باشه
        if normalize:
            result_min = result.min()
            result_max = result.max()
            if result_max - result_min > 1e-6:
                result = (result - result_min) * 255.0 / (result_max - result_min)

        return result.astype(np.uint8)

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

        sobel_x = ConvolutionFilters.convolve_manual(image, kernel_x, "replicate")
        sobel_y = ConvolutionFilters.convolve_manual(image, kernel_y, "replicate")

        # محاسبه Magnitude
        if len(image.shape) == 3:
            magnitude = np.zeros_like(sobel_x)
            for c in range(3):
                magnitude[:, :, c] = np.sqrt(
                    sobel_x[:, :, c] ** 2 + sobel_y[:, :, c] ** 2
                )
        else:
            magnitude = np.sqrt(sobel_x**2 + sobel_y**2)

        return np.clip(magnitude, 0, 255).astype(np.uint8)

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

        prewitt_x = ConvolutionFilters.convolve_manual(image, kernel_x, "replicate")
        prewitt_y = ConvolutionFilters.convolve_manual(image, kernel_y, "replicate")

        if len(image.shape) == 3:
            magnitude = np.zeros_like(prewitt_x)
            for c in range(3):
                magnitude[:, :, c] = np.sqrt(
                    prewitt_x[:, :, c] ** 2 + prewitt_y[:, :, c] ** 2
                )
        else:
            magnitude = np.sqrt(prewitt_x**2 + prewitt_y**2)

        return np.clip(magnitude, 0, 255).astype(np.uint8)

    @staticmethod
    def laplacian_filter(image: np.ndarray, **params) -> np.ndarray:
        """فیلتر Laplacian - لبه‌یابی"""
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
        """Box Blur - میانگین ساده"""
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
        result = ConvolutionFilters.apply_kernel(image, kernel)
        # اضافه کردن 128 برای حالت emboss
        result = np.clip(result.astype(np.int16) + 128, 0, 255).astype(np.uint8)
        return result

    @staticmethod
    def emboss_subtle(image: np.ndarray, **params) -> np.ndarray:
        """افکت Emboss ملایم"""
        kernel = ConvolutionFilters.KERNELS["emboss_subtle"]
        result = ConvolutionFilters.apply_kernel(image, kernel)
        result = np.clip(result.astype(np.int16) + 128, 0, 255).astype(np.uint8)
        return result

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
        """Custom Kernel از کاربر"""
        kernel = params.get("kernel", None)
        normalize = params.get("normalize", False)
        padding = params.get("padding", "replicate")

        if kernel is None:
            kernel = ConvolutionFilters.KERNELS["identity"]

        return ConvolutionFilters.apply_kernel(image, kernel, normalize, padding)


# نقشه فیلترها
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
