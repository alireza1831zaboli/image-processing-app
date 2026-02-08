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
    # Dilation/erosion based local maxima
    kernel = np.ones((window, window), dtype=np.uint8)
    dilated = cv2.dilate(resp, kernel)
    eroded = cv2.erode(resp, kernel)

    # Strict local maxima: equals local max AND strictly greater than local min
    # (this removes flat plateaus that would otherwise create many "maxima").
    maxima = (resp == dilated) & (resp > eroded) & mask

    # Remove NaNs / inf
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
    """Compute Moravec response map.

    PDF version: For each pixel (excluding borders), compute W as mean of 3x3 neighborhood
    at four offsets (-1,1), (0,1), (1,1), (1,0). For each offset, compute E = (I - W)^2
    and take min(E1..E4) as final response.
    """
    g = gray

    # blur of shifted images approximates mean of 3x3 neighborhood at shifted position
    offsets = [(-1, 1), (0, 1), (1, 1), (1, 0)]
    Es = []
    for dx, dy in offsets:
        shifted = np.roll(g, shift=(dy, dx), axis=(0, 1))
        W = cv2.blur(shifted, (3, 3))
        E = (g - W) ** 2
        Es.append(E)

    resp = np.minimum.reduce(Es)

    # Zero borders (where neighborhood would be invalid)
    resp[:1, :] = 0
    resp[-1:, :] = 0
    resp[:, :1] = 0
    resp[:, -1:] = 0
    return resp.astype(np.float32)


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
    points = _nms_local_maxima(resp, mask, window=int(nms_window), max_points=int(max_points))
    return _draw_points(image, points, radius=int(circle_radius), thickness=int(circle_thickness))


# --- Haralick (Hessian-based per assignment) ---

def _haralick_derivatives(gray: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Compute Dxx, Dyy, Dxy per masks described in the assignment PDF."""
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

    # Hessian metrics
    w = (dxx * dyy) - (dxy * dxy)
    trace = dxx + dyy

    # eigenvalues of 2x2 Hessian
    disc = np.sqrt((dxx - dyy) ** 2 + 4.0 * (dxy ** 2))
    lam1 = (trace + disc) / 2.0
    lam2 = (trace - disc) / 2.0

    eps = 1e-9
    denom = (lam1 + lam2)
    ratio = (lam1 - lam2) / (denom + eps)
    q = 1.0 - (ratio ** 2)

    # For scoring we use positive w only (corner-like).
    w_pos = np.maximum(w, 0).astype(np.float32)

    # Threshold for w=det(Hessian). Assignment asks for a user-provided threshold.
    # If thresh_w is 0 (default), we pick a robust auto-threshold using the 99th percentile
    # of positive responses to keep the UI usable across different images.
    w_vals = w_pos[w_pos > 0]
    if w_vals.size == 0:
        return _draw_points(image, np.empty((0, 2), dtype=np.int32), radius=int(circle_radius), thickness=int(circle_thickness))

    w_thr = float(thresh_w)
    if w_thr <= 0:
        w_thr = float(np.percentile(w_vals, 99))

    mask = (w_pos > w_thr) & (q > float(thresh_q))

    points = _nms_local_maxima(w_pos, mask, window=int(nms_window), max_points=int(max_points))
    return _draw_points(image, points, radius=int(circle_radius), thickness=int(circle_thickness))


# --- Harris (assignment formula) ---

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
    R = det - (tr ** 2)

    # Threshold for R. Assignment asks for a user-provided threshold.
    # If threshold_r is 0 (default), pick an auto-threshold from the upper tail.
    R_thr = float(threshold_r)
    if R_thr <= 0:
        R_thr = float(np.percentile(R, 99))

    mask = R > R_thr

    # Use R as score for NMS (mask limits candidates)
    score = R.astype(np.float32)

    points = _nms_local_maxima(score, mask, window=int(nms_window), max_points=int(max_points))
    return _draw_points(image, points, radius=int(circle_radius), thickness=int(circle_thickness))


# Registry for ImageManager
FILTER_MAP = {
    "moravec_corner": moravec_corner,
    "haralick_corner": haralick_corner,
    "harris_corner": harris_corner,
}
