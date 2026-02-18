import cv2
import numpy as np


class EdgeFilters:

    @staticmethod
    def canny(image: np.ndarray, **params) -> np.ndarray:
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

    @staticmethod
    def canny_project4(image: np.ndarray, **params):
        """Canny Edge Detection (Project #4) - step-by-step, manual pipeline.

        1) RGB -> Gray
        2) Gaussian Blur
        3) Sobel X/Y
        4) Magnitude: |G| = sqrt(Gx^2 + Gy^2) (normalized)
        5) Direction: theta = atan(Gy/Gx) (displayed)
        6) Non-Maximum Suppression
        7) Hysteresis Thresholding
        """

        def _norm_u8(arr: np.ndarray) -> np.ndarray:
            arr = arr.astype(np.float32)
            mn = float(np.min(arr))
            mx = float(np.max(arr))
            if mx - mn < 1e-8:
                return np.zeros(arr.shape, dtype=np.uint8)
            out = (arr - mn) / (mx - mn)
            return np.clip(out * 255.0, 0, 255).astype(np.uint8)

        def _non_max_suppression(mag_u8: np.ndarray, theta_rad: np.ndarray) -> np.ndarray:
            h, w = mag_u8.shape
            Z = np.zeros((h, w), dtype=np.uint8)

            angle = np.rad2deg(theta_rad)
            angle[angle < 0] += 180

            for i in range(1, h - 1):
                for j in range(1, w - 1):
                    a = angle[i, j]

                    if (0 <= a < 22.5) or (157.5 <= a <= 180):
                        q = mag_u8[i, j + 1]
                        r = mag_u8[i, j - 1]
                    elif 22.5 <= a < 67.5:
                        q = mag_u8[i + 1, j - 1]
                        r = mag_u8[i - 1, j + 1]
                    elif 67.5 <= a < 112.5:
                        q = mag_u8[i + 1, j]
                        r = mag_u8[i - 1, j]
                    else:  # 112.5..157.5
                        q = mag_u8[i - 1, j - 1]
                        r = mag_u8[i + 1, j + 1]

                    v = mag_u8[i, j]
                    if v >= q and v >= r:
                        Z[i, j] = v
            return Z

        def _hysteresis(nms_u8: np.ndarray, low: int, high: int):
            low = int(max(0, min(255, low)))
            high = int(max(0, min(255, high)))
            if low > high:
                low, high = high, low

            strong = 255
            weak = 128

            res = np.zeros_like(nms_u8, dtype=np.uint8)
            strong_y, strong_x = np.where(nms_u8 >= high)
            weak_y, weak_x = np.where((nms_u8 >= low) & (nms_u8 < high))

            res[strong_y, strong_x] = strong
            res[weak_y, weak_x] = weak

            stack = list(zip(strong_y.tolist(), strong_x.tolist()))
            while stack:
                y, x = stack.pop()
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        if dy == 0 and dx == 0:
                            continue
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < res.shape[0] and 0 <= nx < res.shape[1]:
                            if res[ny, nx] == weak:
                                res[ny, nx] = strong
                                stack.append((ny, nx))

            final_edges = (res == strong).astype(np.uint8) * 255
            return res, final_edges

        low_threshold = int(params.get("low_threshold", 50))
        high_threshold = int(params.get("high_threshold", 150))
        gaussian_ksize = int(params.get("gaussian_ksize", 5))
        if gaussian_ksize < 3:
            gaussian_ksize = 3
        if gaussian_ksize % 2 == 0:
            gaussian_ksize += 1

        # 1) Gray
        gray = (
            cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        )
        gray_u8 = gray.astype(np.uint8)

        # 2) Gaussian Blur
        blur = cv2.GaussianBlur(gray_u8, (gaussian_ksize, gaussian_ksize), 0)

        # 3) Sobel kernels + filtering
        Kx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float32)
        Ky = np.array([[1, 2, 1], [0, 0, 0], [-1, -2, -1]], dtype=np.float32)
        blur_f = blur.astype(np.float32)
        Gx = cv2.filter2D(blur_f, cv2.CV_32F, Kx)
        Gy = cv2.filter2D(blur_f, cv2.CV_32F, Ky)

        sobelx_disp = _norm_u8(np.abs(Gx))
        sobely_disp = _norm_u8(np.abs(Gy))

        # 4) Magnitude
        mag = np.sqrt(Gx * Gx + Gy * Gy)
        mag_u8 = _norm_u8(mag)

        # 5) Direction  θ = atan^{-1}(Gy / Gx)
        # For display and NMS we use the conventional [0..180) degree range.
        theta = np.arctan2(Gy, Gx)
        theta_deg = np.rad2deg(theta)
        theta_deg[theta_deg < 0] += 180.0
        dir_disp = np.clip((theta_deg / 180.0) * 255.0, 0, 255).astype(np.uint8)

        # 6) NMS
        nms = _non_max_suppression(mag_u8, theta)

        # 7) Hysteresis
        _thresh_map, edges_u8 = _hysteresis(nms, low_threshold, high_threshold)

        stages = [
            ("1) RGB → Grayscale", gray_u8),
            (f"2) Gaussian Blur ({gaussian_ksize}×{gaussian_ksize})", blur),
            ("3) Sobel X", sobelx_disp),
            ("3) Sobel Y", sobely_disp),
            ("4) Gradient Magnitude |G|", mag_u8),
            ("5) Gradient Direction θ", dir_disp),
            ("6) Non-Maximum Suppression", nms),
            ("7) Hysteresis Thresholding (Final Edges)", edges_u8),
        ]

        final_out = (
            cv2.cvtColor(edges_u8, cv2.COLOR_GRAY2BGR)
            if len(image.shape) == 3
            else edges_u8
        )

        return {"result": final_out, "stages": stages}


FILTER_MAP = {
    "edge_canny": EdgeFilters.canny,
    "edge_canny_project4": EdgeFilters.canny_project4,
    "edge_sobel": EdgeFilters.sobel,
    "edge_laplacian": EdgeFilters.laplacian,
    "edge_scharr": EdgeFilters.scharr,
}
