"""Point Detection filters: Moravec, Haralick, Harris.

Each filter returns an image with detected points drawn as red circles.
"""

from __future__ import annotations

from typing import Tuple

import cv2
import numpy as np


def _to_gray(image: np.ndarray) -> np.ndarray:
    """Convert BGR (OpenCV default) or gray to single-channel float32."""
    if image is None:
        raise ValueError("image is None")
    if image.ndim == 2:
        gray = image
    elif image.ndim == 3 and image.shape[2] == 3:
        # Treat input as BGR (OpenCV convention in this project)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        raise ValueError(f"Unsupported image shape: {getattr(image, 'shape', None)}")

    return gray.astype(np.float32)


def _ensure_bgr(image: np.ndarray) -> np.ndarray:
    """Ensure output is 3-channel BGR (for drawing red circles)."""
    if image.ndim == 2:
        return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    if image.ndim == 3 and image.shape[2] == 3:
        return image
    raise ValueError(f"Unsupported image shape: {getattr(image, 'shape', None)}")


def _nms_local_maxima(
    response: np.ndarray,
    mask: np.ndarray,
    window: int = 7,
    max_points: int = 0,
) -> np.ndarray:
    """Non-maximum suppression via dilation.

    Args:
        response: float32 response map.
        mask: boolean mask of eligible pixels (thresholding etc.).
        window: odd integer window size.
        max_points: if >0, keep only top-N points by response.

    Returns:
        points: array of shape (N, 2) with (x, y).
    """
    if window < 1:
        window = 1
    if window % 2 == 0:
        window += 1

    resp = response.astype(np.float32)
    kernel = np.ones((window, window), dtype=np.uint8)
    dilated = cv2.dilate(resp, kernel)
    eroded = cv2.erode(resp, kernel)

    maxima = (resp == dilated) & (resp > eroded) & mask

    maxima &= np.isfinite(resp)

    ys, xs = np.where(maxima)
    if xs.size == 0:
        return np.empty((0, 2), dtype=np.int32)

    if max_points and max_points > 0 and xs.size > max_points:
        scores = resp[ys, xs]
        idx = np.argpartition(scores, -max_points)[-max_points:]
        # sort descending for stability
        idx = idx[np.argsort(scores[idx])[::-1]]
        xs = xs[idx]
        ys = ys[idx]

    return np.stack([xs, ys], axis=1).astype(np.int32)


def _draw_points(
    base_image: np.ndarray,
    points: np.ndarray,
    radius: int = 3,
    thickness: int = 1,
) -> np.ndarray:
    out = _ensure_bgr(base_image.copy())
    if radius < 1:
        radius = 1
    if thickness < 1:
        thickness = 1

    for x, y in points:
        cv2.circle(out, (int(x), int(y)), int(radius), (0, 0, 255), int(thickness))

    return out


# --- Moravec ---


def _moravec_response(gray: np.ndarray) -> np.ndarray:
    g = gray.astype(np.float32)

    pad = 1
    gp = cv2.copyMakeBorder(g, pad, pad, pad, pad, borderType=cv2.BORDER_REFLECT101)
    mean_map = cv2.blur(gp, (3, 3))

    h, w = g.shape[:2]
    offsets = [(-1, 1), (0, 1), (1, 1), (1, 0)]
    Es = []
    for dx, dy in offsets:
        Wm = mean_map[pad + dy : pad + dy + h, pad + dx : pad + dx + w]
        Es.append((g - Wm) ** 2)

    resp = np.minimum.reduce(Es).astype(np.float32)

    valid = np.zeros_like(resp, dtype=bool)
    if h >= 4 and w >= 5:
        valid[1 : h - 2, 2 : w - 2] = True
    resp[~valid] = 0.0
    return resp


def moravec_corner(
    image: np.ndarray,
    threshold: float = 1000.0,
    nms_window: int = 7,
    circle_radius: int = 3,
    circle_thickness: int = 1,
    max_points: int = 0,
) -> np.ndarray:
    gray = _to_gray(image)
    resp = _moravec_response(gray)

    mask = resp > float(threshold)
    points = _nms_local_maxima(
        resp, mask, window=int(nms_window), max_points=int(max_points)
    )
    return _draw_points(
        image, points, radius=int(circle_radius), thickness=int(circle_thickness)
    )


# --- Haralick (Hessian-based per assignment) ---


def _haralick_derivatives(
    gray: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    g = gray

    Dxx_k = np.array([[1, -2, 1], [1, -2, 1], [1, -2, 1]], dtype=np.float32)
    Dyy_k = np.array([[1, 1, 1], [-2, -2, -2], [1, 1, 1]], dtype=np.float32)

    DxL_k = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]], dtype=np.float32)
    DxR_k = np.array([[1, 0, -1], [1, 0, -1], [1, 0, -1]], dtype=np.float32)

    DyU_k = np.array([[-1, -1, -1], [0, 0, 0], [1, 1, 1]], dtype=np.float32)
    DyD_k = np.array([[1, 1, 1], [0, 0, 0], [-1, -1, -1]], dtype=np.float32)

    dxx = cv2.filter2D(g, ddepth=cv2.CV_32F, kernel=Dxx_k)
    dyy = cv2.filter2D(g, ddepth=cv2.CV_32F, kernel=Dyy_k)

    dxL = cv2.filter2D(g, ddepth=cv2.CV_32F, kernel=DxL_k)
    dxR = cv2.filter2D(g, ddepth=cv2.CV_32F, kernel=DxR_k)
    dyU = cv2.filter2D(g, ddepth=cv2.CV_32F, kernel=DyU_k)
    dyD = cv2.filter2D(g, ddepth=cv2.CV_32F, kernel=DyD_k)

    Dx = np.maximum(dxL, dxR)
    Dy = np.maximum(dyU, dyD)
    dxy = np.maximum(Dx, Dy)

    return dxx, dyy, dxy


def haralick_corner(
    image: np.ndarray,
    thresh_w: float = 0.0,
    thresh_q: float = 0.5,
    nms_window: int = 7,
    circle_radius: int = 3,
    circle_thickness: int = 1,
    max_points: int = 0,
) -> np.ndarray:
    gray = _to_gray(image)
    dxx, dyy, dxy = _haralick_derivatives(gray)

    w = (dxx * dyy) - (dxy * dxy)
    trace = dxx + dyy

    disc = np.sqrt((dxx - dyy) ** 2 + 4.0 * (dxy**2))
    lam1 = (trace + disc) / 2.0
    lam2 = (trace - disc) / 2.0

    eps = 1e-9
    denom = lam1 + lam2
    ratio = (lam1 - lam2) / (denom + eps)
    q = 1.0 - (ratio**2)

    w_pos = np.maximum(w, 0).astype(np.float32)

    w_vals = w_pos[w_pos > 0]
    if w_vals.size == 0:
        return _draw_points(
            image,
            np.empty((0, 2), dtype=np.int32),
            radius=int(circle_radius),
            thickness=int(circle_thickness),
        )

    w_thr = float(thresh_w)
    if w_thr <= 0:
        w_thr = float(np.percentile(w_vals, 99))

    mask = (w_pos > w_thr) & (q > float(thresh_q))

    points = _nms_local_maxima(
        w_pos, mask, window=int(nms_window), max_points=int(max_points)
    )
    return _draw_points(
        image, points, radius=int(circle_radius), thickness=int(circle_thickness)
    )


# --- Harris ---


def harris_corner(
    image: np.ndarray,
    threshold_r: float = 0.0,
    gaussian_ksize: int = 5,
    gaussian_sigma: float = 1.0,
    nms_window: int = 7,
    circle_radius: int = 3,
    circle_thickness: int = 1,
    max_points: int = 0,
) -> np.ndarray:
    gray = _to_gray(image)

    k = int(gaussian_ksize)
    if k < 3:
        k = 3
    if k % 2 == 0:
        k += 1

    blurred = cv2.GaussianBlur(gray, (k, k), float(gaussian_sigma))
    dxx, dyy, dxy = _haralick_derivatives(blurred)

    det = (dxx * dyy) - (dxy * dxy)
    tr = dxx + dyy
    R = (det - (tr * tr)).astype(np.float32)

    score = (-R).astype(np.float32)

    finite = np.isfinite(score)
    thr = float(threshold_r)
    mask = finite & (score > thr)

    points = _nms_local_maxima(
        score, mask, window=int(nms_window), max_points=int(max_points)
    )
    return _draw_points(
        image, points, radius=int(circle_radius), thickness=int(circle_thickness)
    )


FILTER_MAP = {
    "moravec_corner": moravec_corner,
    "haralick_corner": haralick_corner,
    "harris_corner": harris_corner,
}
