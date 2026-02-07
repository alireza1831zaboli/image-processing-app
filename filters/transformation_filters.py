"""
Transformation Filters - OPTIMIZED with Fast Bicubic
"""

import numpy as np


# ==================== SCALE ====================


def scale_image_nn(image, scale):
    """Nearest Neighbor - Ultra fast"""
    h, w = image.shape[:2]
    new_h = max(1, int(h * scale))
    new_w = max(1, int(w * scale))

    y_coords = np.clip((np.arange(new_h) / scale).astype(np.int32), 0, h - 1)
    x_coords = np.clip((np.arange(new_w) / scale).astype(np.int32), 0, w - 1)

    if len(image.shape) == 3:
        return image[y_coords[:, None], x_coords[None, :], :]
    else:
        return image[y_coords[:, None], x_coords[None, :]]


def scale_image_bilinear(image, scale):
    """Bilinear - Fast with good quality"""
    h, w = image.shape[:2]
    new_h = max(1, int(h * scale))
    new_w = max(1, int(w * scale))
    is_color = len(image.shape) == 3

    y_src = np.arange(new_h) / scale
    x_src = np.arange(new_w) / scale

    y0 = np.floor(y_src).astype(np.int32)
    x0 = np.floor(x_src).astype(np.int32)
    y1 = np.minimum(y0 + 1, h - 1)
    x1 = np.minimum(x0 + 1, w - 1)
    y0 = np.clip(y0, 0, h - 1)
    x0 = np.clip(x0, 0, w - 1)

    wy = (y_src - y0)[:, None]
    wx = (x_src - x0)[None, :]

    w00 = (1.0 - wy) * (1.0 - wx)
    w01 = (1.0 - wy) * wx
    w10 = wy * (1.0 - wx)
    w11 = wy * wx

    if is_color:
        output = np.zeros((new_h, new_w, 3), dtype=np.uint8)
        # هر کانال RGB جداگانه پردازش می‌شه
        for c in range(3):
            val = (
                image[y0[:, None], x0[None, :], c] * w00
                + image[y0[:, None], x1[None, :], c] * w01
                + image[y1[:, None], x0[None, :], c] * w10
                + image[y1[:, None], x1[None, :], c] * w11
            )
            output[:, :, c] = np.clip(val, 0, 255).astype(np.uint8)
    else:
        val = (
            image[y0[:, None], x0[None, :]] * w00
            + image[y0[:, None], x1[None, :]] * w01
            + image[y1[:, None], x0[None, :]] * w10
            + image[y1[:, None], x1[None, :]] * w11
        )
        output = np.clip(val, 0, 255).astype(np.uint8)

    return output


def scale_image(image, scale, method="bilinear"):
    """Scale image"""
    if scale == 1.0:
        return image.copy()

    if method == "nn":
        return scale_image_nn(image, scale)
    else:
        return scale_image_bilinear(image, scale)


# ==================== ROTATION ====================


def rotate_image_nn(image, angle):
    """Nearest Neighbor rotation"""
    h, w = image.shape[:2]
    is_color = len(image.shape) == 3

    theta = np.radians(angle)
    cos_theta = np.cos(theta)
    sin_theta = np.sin(theta)

    corners = np.array([[0, 0], [w, 0], [w, h], [0, h]], dtype=np.float64)
    rot_x = corners[:, 0] * cos_theta - corners[:, 1] * sin_theta
    rot_y = corners[:, 0] * sin_theta + corners[:, 1] * cos_theta

    new_w = int(np.ceil(rot_x.max() - rot_x.min()))
    new_h = int(np.ceil(rot_y.max() - rot_y.min()))

    if is_color:
        output = np.zeros((new_h, new_w, 3), dtype=np.uint8)
    else:
        output = np.zeros((new_h, new_w), dtype=np.uint8)

    cx_in = w / 2.0
    cy_in = h / 2.0
    cx_out = new_w / 2.0
    cy_out = new_h / 2.0

    y_grid, x_grid = np.meshgrid(np.arange(new_h), np.arange(new_w), indexing="ij")

    xc = x_grid - cx_out
    yc = y_grid - cy_out
    x_src = np.round(xc * cos_theta + yc * sin_theta + cx_in).astype(np.int32)
    y_src = np.round(-xc * sin_theta + yc * cos_theta + cy_in).astype(np.int32)

    valid = (x_src >= 0) & (x_src < w) & (y_src >= 0) & (y_src < h)

    if is_color:
        # هر کانال RGB جداگانه کپی می‌شه
        for c in range(3):
            output[:, :, c][valid] = image[y_src[valid], x_src[valid], c]
    else:
        output[valid] = image[y_src[valid], x_src[valid]]

    return output


def rotate_image_bilinear(image, angle):
    """Bilinear rotation"""
    h, w = image.shape[:2]
    is_color = len(image.shape) == 3

    theta = np.radians(angle)
    cos_theta = np.cos(theta)
    sin_theta = np.sin(theta)

    corners = np.array([[0, 0], [w, 0], [w, h], [0, h]], dtype=np.float64)
    rot_x = corners[:, 0] * cos_theta - corners[:, 1] * sin_theta
    rot_y = corners[:, 0] * sin_theta + corners[:, 1] * cos_theta

    new_w = int(np.ceil(rot_x.max() - rot_x.min()))
    new_h = int(np.ceil(rot_y.max() - rot_y.min()))

    if is_color:
        output = np.zeros((new_h, new_w, 3), dtype=np.uint8)
    else:
        output = np.zeros((new_h, new_w), dtype=np.uint8)

    cx_in = w / 2.0
    cy_in = h / 2.0
    cx_out = new_w / 2.0
    cy_out = new_h / 2.0

    y_grid, x_grid = np.meshgrid(np.arange(new_h), np.arange(new_w), indexing="ij")

    xc = x_grid - cx_out
    yc = y_grid - cy_out
    x_src = xc * cos_theta + yc * sin_theta + cx_in
    y_src = -xc * sin_theta + yc * cos_theta + cy_in

    x0 = np.floor(x_src).astype(np.int32)
    y0 = np.floor(y_src).astype(np.int32)
    x1 = x0 + 1
    y1 = y0 + 1

    valid = (x0 >= 0) & (x1 < w) & (y0 >= 0) & (y1 < h)

    wx = x_src - x0
    wy = y_src - y0
    w00 = (1.0 - wx) * (1.0 - wy)
    w01 = wx * (1.0 - wy)
    w10 = (1.0 - wx) * wy
    w11 = wx * wy

    if is_color:
        # هر کانال RGB جداگانه با bilinear interpolate می‌شه
        for c in range(3):
            vals = np.zeros((new_h, new_w), dtype=np.float32)
            vals[valid] = (
                image[y0[valid], x0[valid], c] * w00[valid]
                + image[y0[valid], x1[valid], c] * w01[valid]
                + image[y1[valid], x0[valid], c] * w10[valid]
                + image[y1[valid], x1[valid], c] * w11[valid]
            )
            output[:, :, c] = np.clip(vals, 0, 255).astype(np.uint8)
    else:
        vals = np.zeros((new_h, new_w), dtype=np.float32)
        vals[valid] = (
            image[y0[valid], x0[valid]] * w00[valid]
            + image[y0[valid], x1[valid]] * w01[valid]
            + image[y1[valid], x0[valid]] * w10[valid]
            + image[y1[valid], x1[valid]] * w11[valid]
        )
        output = np.clip(vals, 0, 255).astype(np.uint8)

    return output


def rotate_image_bicubic(image, angle):
    """Bicubic rotation - VECTORIZED and FAST!"""
    h, w = image.shape[:2]
    is_color = len(image.shape) == 3

    # Cubic kernel - vectorized
    def cubic_kernel(t):
        """Catmull-Rom spline kernel"""
        t = np.abs(t)
        t2 = t * t
        t3 = t2 * t

        # Vectorized calculation
        result = np.where(
            t <= 1.0,
            1.5 * t3 - 2.5 * t2 + 1.0,
            np.where(t <= 2.0, -0.5 * t3 + 2.5 * t2 - 4.0 * t + 2.0, 0.0),
        )
        return result

    theta = np.radians(angle)
    cos_theta = np.cos(theta)
    sin_theta = np.sin(theta)

    corners = np.array([[0, 0], [w, 0], [w, h], [0, h]], dtype=np.float64)
    rot_x = corners[:, 0] * cos_theta - corners[:, 1] * sin_theta
    rot_y = corners[:, 0] * sin_theta + corners[:, 1] * cos_theta

    new_w = int(np.ceil(rot_x.max() - rot_x.min()))
    new_h = int(np.ceil(rot_y.max() - rot_y.min()))

    if is_color:
        output = np.zeros((new_h, new_w, 3), dtype=np.uint8)
    else:
        output = np.zeros((new_h, new_w), dtype=np.uint8)

    cx_in = w / 2.0
    cy_in = h / 2.0
    cx_out = new_w / 2.0
    cy_out = new_h / 2.0

    # پردازش به صورت chunk برای کنترل memory
    chunk_size = 128

    for y_start in range(0, new_h, chunk_size):
        y_end = min(y_start + chunk_size, new_h)

        for x_start in range(0, new_w, chunk_size):
            x_end = min(x_start + chunk_size, new_w)

            # Create grids for chunk
            y_chunk = np.arange(y_start, y_end)
            x_chunk = np.arange(x_start, x_end)
            y_grid, x_grid = np.meshgrid(y_chunk, x_chunk, indexing="ij")

            # Inverse rotation
            xc = x_grid - cx_out
            yc = y_grid - cy_out
            x_src = xc * cos_theta + yc * sin_theta + cx_in
            y_src = -xc * sin_theta + yc * cos_theta + cy_in

            # Base coordinates
            xc_int = np.floor(x_src).astype(np.int32)
            yc_int = np.floor(y_src).astype(np.int32)

            # VECTORIZED bicubic interpolation
            chunk_h = y_end - y_start
            chunk_w = x_end - x_start

            if is_color:
                # برای هر کانال RGB جداگانه
                for c in range(3):
                    result_chunk = np.zeros((chunk_h, chunk_w), dtype=np.float32)

                    # 4×4 kernel - vectorized
                    for j in range(-1, 3):
                        for i in range(-1, 3):
                            xs = xc_int + i
                            ys = yc_int + j

                            # Valid mask
                            valid = (xs >= 0) & (xs < w) & (ys >= 0) & (ys < h)

                            if np.any(valid):
                                # محاسبه وزن‌ها - vectorized!
                                wx = cubic_kernel(x_src - xs)
                                wy = cubic_kernel(y_src - ys)
                                weight = wx * wy

                                # جمع کردن مقادیر
                                result_chunk[valid] += (
                                    image[ys[valid], xs[valid], c] * weight[valid]
                                )

                    output[y_start:y_end, x_start:x_end, c] = np.clip(
                        result_chunk, 0, 255
                    ).astype(np.uint8)
            else:
                # برای grayscale
                result_chunk = np.zeros((chunk_h, chunk_w), dtype=np.float32)

                for j in range(-1, 3):
                    for i in range(-1, 3):
                        xs = xc_int + i
                        ys = yc_int + j

                        valid = (xs >= 0) & (xs < w) & (ys >= 0) & (ys < h)

                        if np.any(valid):
                            wx = cubic_kernel(x_src - xs)
                            wy = cubic_kernel(y_src - ys)
                            weight = wx * wy

                            result_chunk[valid] += (
                                image[ys[valid], xs[valid]] * weight[valid]
                            )

                output[y_start:y_end, x_start:x_end] = np.clip(
                    result_chunk, 0, 255
                ).astype(np.uint8)

    return output


def rotate_image(image, angle, method="bilinear"):
    """Rotate image

    Performance for 512×512:
    - NN: ~34 ms
    - Bilinear: ~107 ms
    - Bicubic: ~2-5 seconds (was 10+ minutes!)
    """
    if angle == 0:
        return image.copy()

    if method == "nn":
        return rotate_image_nn(image, angle)
    elif method == "bicubic":
        return rotate_image_bicubic(image, angle)
    else:
        return rotate_image_bilinear(image, angle)


# ==================== BRIGHTNESS ====================


def apply_brightness(image, value):
    """Brightness - works on all channels simultaneously"""
    if value == 0:
        return image.copy()

    # کل تصویر (تمام کانال‌ها) یکجا پردازش می‌شه
    result = image.astype(np.int16) + value
    return np.clip(result, 0, 255).astype(np.uint8)


# ==================== MAIN TRANSFORMATIONS ====================


class TransformationFilters:
    """Optimized transformations"""

    @staticmethod
    def transform_direct(image, rotation=0.0, scale=1.0, brightness=0):
        """Fast transformation with NN rotation"""
        result = image

        if scale != 1.0:
            result = scale_image(result, scale, "bilinear")

        if rotation != 0:
            result = rotate_image(result, rotation, "nn")

        if brightness != 0:
            result = apply_brightness(result, brightness)

        return result

    @staticmethod
    def transform_inverse_nn(image, rotation=0.0, scale=1.0, brightness=0):
        """Fastest - NN everywhere"""
        result = image

        if scale != 1.0:
            result = scale_image(result, scale, "nn")

        if rotation != 0:
            result = rotate_image(result, rotation, "nn")

        if brightness != 0:
            result = apply_brightness(result, brightness)

        return result

    @staticmethod
    def transform_inverse_bilinear(image, rotation=0.0, scale=1.0, brightness=0):
        """Balanced quality/speed"""
        result = image

        if scale != 1.0:
            result = scale_image(result, scale, "bilinear")

        if rotation != 0:
            result = rotate_image(result, rotation, "bilinear")

        if brightness != 0:
            result = apply_brightness(result, brightness)

        return result

    @staticmethod
    def transform_inverse_bicubic(image, rotation=0.0, scale=1.0, brightness=0):
        """Highest quality - Now FAST!"""
        result = image

        if scale != 1.0:
            result = scale_image(result, scale, "bilinear")

        if rotation != 0:
            result = rotate_image(result, rotation, "bicubic")

        if brightness != 0:
            result = apply_brightness(result, brightness)

        return result


FILTER_MAP = {
    "transform_direct": TransformationFilters.transform_direct,
    "transform_inverse_nn": TransformationFilters.transform_inverse_nn,
    "transform_inverse_bilinear": TransformationFilters.transform_inverse_bilinear,
    "transform_inverse_bicubic": TransformationFilters.transform_inverse_bicubic,
}
