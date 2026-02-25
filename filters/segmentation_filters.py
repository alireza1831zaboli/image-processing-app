from __future__ import annotations
import heapq
from typing import Tuple
import cv2
import numpy as np


def _ensure_gray(image: np.ndarray) -> np.ndarray:
    if image is None or image.size == 0:
        return image
    if len(image.shape) == 2:
        return image
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def _odd_ksize(v: int, mn: int = 1, mx: int = 99) -> int:
    v = int(v)
    v = max(mn, min(mx, v))
    if v % 2 == 0:
        v += 1
    return v


def _make_markers_from_otsu(
    gray: np.ndarray,
    blur_ksize: int,
    morph_ksize: int,
    dist_ratio: float,
    dilate_iter: int,
) -> Tuple[np.ndarray, np.ndarray]:
    blur_ksize = _odd_ksize(blur_ksize, 1, 31)
    morph_ksize = _odd_ksize(morph_ksize, 1, 31)
    dilate_iter = int(max(1, min(10, dilate_iter)))

    gray_blur = cv2.GaussianBlur(gray, (blur_ksize, blur_ksize), 0)

    _, thresh = cv2.threshold(gray_blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    border = np.concatenate(
        [
            thresh[0, :],
            thresh[-1, :],
            thresh[:, 0],
            thresh[:, -1],
        ]
    )
    if float(border.mean()) > 127.0:
        thresh = cv2.bitwise_not(thresh)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (morph_ksize, morph_ksize))
    opened = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)

    sure_bg = cv2.dilate(opened, kernel, iterations=dilate_iter)

    dist = cv2.distanceTransform(opened, cv2.DIST_L2, 5)
    dmax = float(dist.max()) if dist is not None else 0.0
    if dmax <= 0:
        markers = np.ones(gray.shape, dtype=np.int32)
        return markers, opened

    dist_ratio = float(max(0.05, min(0.95, dist_ratio)))
    _, sure_fg = cv2.threshold(dist, dist_ratio * dmax, 255, 0)
    sure_fg = sure_fg.astype(np.uint8)

    unknown = cv2.subtract(sure_bg, sure_fg)

    n_labels, markers = cv2.connectedComponents(sure_fg)
    markers = markers.astype(np.int32)

    markers = markers + 1
    markers[unknown == 255] = 0

    return markers, opened


def _make_markers_from_kmeans_seeds(
    image_bgr: np.ndarray,
    k: int,
    blur_ksize: int,
    seed_erosion_iter: int,
    min_seed_area: int,
) -> np.ndarray:
    """Create sparse markers by clustering colors and eroding each cluster to get "sure" seeds.

    Why this helps:
      - Otsu+distance-transform seeds can fail on textured objects (e.g., stone buildings).
      - K-Means provides multiple coarse regions, then erosion makes them sparse markers,
        leaving uncertain boundary pixels as 0 for the watershed flooding stage.

    Returns: markers:int32 with values {0, 1..K}
    """
    if image_bgr is None or image_bgr.size == 0:
        return np.ones((1, 1), dtype=np.int32)

    k = int(max(2, min(12, k)))
    blur_ksize = _odd_ksize(blur_ksize, 1, 31)
    seed_erosion_iter = int(max(0, min(15, seed_erosion_iter)))
    min_seed_area = int(max(0, min(20000, min_seed_area)))

    img = image_bgr.copy()
    if blur_ksize >= 3:
        img = cv2.GaussianBlur(img, (blur_ksize, blur_ksize), 0)

    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    Z = lab.reshape((-1, 3)).astype(np.float32)

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 1.0)
    _, labels, _ = cv2.kmeans(Z, k, None, criteria, 2, cv2.KMEANS_PP_CENTERS)
    labels = labels.reshape((img.shape[0], img.shape[1])).astype(np.int32)

    markers = np.zeros((img.shape[0], img.shape[1]), dtype=np.int32)
    if seed_erosion_iter == 0:
        # Still keep sparse seeds by doing at least a tiny erosion-like effect via open(1).
        seed_erosion_iter = 1

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    current_label = 1
    for c in range(k):
        mask = (labels == c).astype(np.uint8) * 255
        if seed_erosion_iter > 0:
            mask = cv2.erode(mask, kernel, iterations=seed_erosion_iter)
        area = int(cv2.countNonZero(mask))
        if area <= min_seed_area:
            continue
        markers[mask > 0] = current_label
        current_label += 1

    # Fallback: if erosion killed everything, use a gentler erosion
    if markers.max() == 0:
        for c in range(k):
            mask = (labels == c).astype(np.uint8) * 255
            mask = cv2.erode(mask, kernel, iterations=1)
            if cv2.countNonZero(mask) > 0:
                markers[mask > 0] = c + 1

    return markers


def _gradient_magnitude(
    gray: np.ndarray, blur_ksize: int, sobel_ksize: int
) -> np.ndarray:
    blur_ksize = _odd_ksize(blur_ksize, 1, 31)
    sobel_ksize = _odd_ksize(sobel_ksize, 1, 7)
    gray_blur = cv2.GaussianBlur(gray, (blur_ksize, blur_ksize), 0)

    gx = cv2.Sobel(gray_blur, cv2.CV_32F, 1, 0, ksize=sobel_ksize)
    gy = cv2.Sobel(gray_blur, cv2.CV_32F, 0, 1, ksize=sobel_ksize)
    grad = cv2.magnitude(gx, gy)

    grad_u8 = cv2.normalize(grad, None, 0, 255, cv2.NORM_MINMAX)
    return grad_u8.astype(np.uint8)


def _watershed_manual(
    grad_u8: np.ndarray, markers: np.ndarray, connectivity: int = 4
) -> np.ndarray:
    """
    Marker-based watershed flooding (manual implementation).

    We treat grad_u8 as a topographic relief:
      - Low values: basins
      - High values: ridges/edges
    Starting from labeled markers, we flood increasing gradient levels and
    build dams (label -1) where different basins would merge.
    """
    if grad_u8 is None or grad_u8.size == 0:
        return markers.astype(np.int32)

    h, w = grad_u8.shape
    labels = markers.astype(np.int32).copy()
    WATERSHED = -1

    if connectivity == 8:
        nbs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    else:
        nbs = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    in_queue = np.zeros((h, w), dtype=bool)
    pq = []

    # Initialize PQ with unlabeled neighbors of markers
    for y in range(h):
        for x in range(w):
            if labels[y, x] > 0:
                for dy, dx in nbs:
                    ny, nx = y + dy, x + dx
                    if (
                        0 <= ny < h
                        and 0 <= nx < w
                        and labels[ny, nx] == 0
                        and not in_queue[ny, nx]
                    ):
                        heapq.heappush(pq, (int(grad_u8[ny, nx]), ny, nx))
                        in_queue[ny, nx] = True

    while pq:
        _, y, x = heapq.heappop(pq)

        if labels[y, x] != 0:
            continue

        neighbor_labels = set()
        for dy, dx in nbs:
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w:
                lbl = labels[ny, nx]
                if lbl > 0:
                    neighbor_labels.add(int(lbl))

        if len(neighbor_labels) == 1:
            labels[y, x] = next(iter(neighbor_labels))
        elif len(neighbor_labels) > 1:
            labels[y, x] = WATERSHED
        else:
            # Still unknown; keep it for now (rare, but can happen with empty markers).
            continue

        # Push its neighbors
        for dy, dx in nbs:
            ny, nx = y + dy, x + dx
            if (
                0 <= ny < h
                and 0 <= nx < w
                and labels[ny, nx] == 0
                and not in_queue[ny, nx]
            ):
                heapq.heappush(pq, (int(grad_u8[ny, nx]), ny, nx))
                in_queue[ny, nx] = True

    return labels


class SegmentationFilters:
    @staticmethod
    def seg_watershed_manual(image: np.ndarray, **params) -> np.ndarray:
        """
        Watershed segmentation (manual implementation).
        Output: original image with watershed boundaries (dams) overlaid in red.
        """
        if image is None or image.size == 0:
            return image

        # Smoothing / gradient
        blur_ksize = params.get("blur_ksize", 7)
        sobel_ksize = params.get("sobel_ksize", 3)

        # Marker (seed) strategy
        k_markers = int(params.get("k_markers", 6))
        seed_erosion_iter = int(params.get("seed_erosion_iter", 3))
        min_seed_area = int(params.get("min_seed_area", 80))

        # Flooding behavior / output
        connectivity_raw = int(params.get("connectivity", 4))
        connectivity = 8 if connectivity_raw >= 6 else 4
        boundary_thickness = int(max(1, min(7, params.get("boundary_thickness", 2))))
        overlay_alpha = float(max(0.0, min(1.0, params.get("overlay_alpha", 0.9))))

        img_bgr = image.copy()
        if len(img_bgr.shape) == 2:
            img_bgr = cv2.cvtColor(img_bgr, cv2.COLOR_GRAY2BGR)

        gray = _ensure_gray(img_bgr)

        # More robust markers for textured scenes: kmeans → erode → sparse seeds
        markers = _make_markers_from_kmeans_seeds(
            img_bgr,
            k=k_markers,
            blur_ksize=blur_ksize,
            seed_erosion_iter=seed_erosion_iter,
            min_seed_area=min_seed_area,
        )
        if markers is None or markers.size == 0 or int(markers.max()) == 0:
            # Final fallback to Otsu-based markers
            morph_ksize = params.get("morph_ksize", 3)
            dist_ratio = params.get("dist_ratio", 0.4)
            dilate_iter = params.get("dilate_iter", 3)
            markers, _ = _make_markers_from_otsu(
                gray, blur_ksize, morph_ksize, dist_ratio, dilate_iter
            )

        grad_u8 = _gradient_magnitude(gray, blur_ksize, sobel_ksize)
        labels = _watershed_manual(grad_u8, markers, connectivity=connectivity)

        # Build a thicker boundary mask
        boundary = (labels == -1).astype(np.uint8) * 255
        if boundary_thickness > 1:
            k = cv2.getStructuringElement(
                cv2.MORPH_ELLIPSE, (boundary_thickness, boundary_thickness)
            )
            boundary = cv2.dilate(boundary, k, iterations=1)

        # Alpha overlay (red boundary)
        out = img_bgr.copy()
        if overlay_alpha > 0 and boundary is not None:
            red = out.copy()
            red[boundary > 0] = (0, 0, 255)
            out = cv2.addWeighted(red, overlay_alpha, out, 1.0 - overlay_alpha, 0)

        return out

    @staticmethod
    def seg_watershed_opencv(image: np.ndarray, **params) -> np.ndarray:
        """
        Watershed segmentation using OpenCV cv2.watershed (reference).

        Important: cv2.watershed is very sensitive to how markers are built.
        This implementation supports two marker strategies:

          - marker_mode='kmeans' (default): color K-Means → erode → sparse "sure" seeds
            Works better on textured scenes (e.g., stone buildings).
          - marker_mode='otsu': Otsu + morphology + distance-transform (classic demo approach)

        Output: original image with watershed boundaries overlaid in red.
        """
        if image is None or image.size == 0:
            return image

        # Output controls
        boundary_thickness = int(max(1, min(7, params.get("boundary_thickness", 2))))
        overlay_alpha = float(max(0.0, min(1.0, params.get("overlay_alpha", 0.9))))

        # cv2.watershed expects 3-channel BGR
        img_bgr = image.copy()
        if len(img_bgr.shape) == 2:
            img_bgr = cv2.cvtColor(img_bgr, cv2.COLOR_GRAY2BGR)

        gray = _ensure_gray(img_bgr)

        marker_mode = str(params.get("marker_mode", "kmeans")).lower().strip()

        if marker_mode == "otsu":
            blur_ksize = params.get("blur_ksize", 7)
            morph_ksize = params.get("morph_ksize", 3)
            dist_ratio = params.get("dist_ratio", 0.4)
            dilate_iter = params.get("dilate_iter", 3)
            markers, _ = _make_markers_from_otsu(
                gray, blur_ksize, morph_ksize, dist_ratio, dilate_iter
            )
        else:
            # Default: robust marker seeds via K-Means clustering
            blur_ksize = params.get("blur_ksize", 7)
            k_markers = int(params.get("k_markers", 7))
            seed_erosion_iter = int(params.get("seed_erosion_iter", 2))
            min_seed_area = int(params.get("min_seed_area", 60))

            markers = _make_markers_from_kmeans_seeds(
                img_bgr,
                k=k_markers,
                blur_ksize=blur_ksize,
                seed_erosion_iter=seed_erosion_iter,
                min_seed_area=min_seed_area,
            )

            # If kmeans markers are empty, fall back to otsu markers automatically
            if markers is None or markers.size == 0 or int(markers.max()) == 0:
                morph_ksize = params.get("morph_ksize", 3)
                dist_ratio = params.get("dist_ratio", 0.4)
                dilate_iter = params.get("dilate_iter", 3)
                markers, _ = _make_markers_from_otsu(
                    gray, blur_ksize, morph_ksize, dist_ratio, dilate_iter
                )

        markers_ws = markers.astype(np.int32).copy()
        cv2.watershed(img_bgr, markers_ws)

        boundary = (markers_ws == -1).astype(np.uint8) * 255
        if boundary_thickness > 1:
            k = cv2.getStructuringElement(
                cv2.MORPH_ELLIPSE, (boundary_thickness, boundary_thickness)
            )
            boundary = cv2.dilate(boundary, k, iterations=1)

        out = img_bgr.copy()
        if overlay_alpha > 0:
            red = out.copy()
            red[boundary > 0] = (0, 0, 255)
            out = cv2.addWeighted(red, overlay_alpha, out, 1.0 - overlay_alpha, 0)

        return out

    @staticmethod
    def seg_kmeans(image: np.ndarray, **params) -> np.ndarray:
        """
        K-Means segmentation using OpenCV kmeans over color (or grayscale) features.
        Output: quantized (clustered) image.
        """
        if image is None or image.size == 0:
            return image

        k = int(params.get("k", 6))
        k = max(2, min(20, k))

        img = image.copy()
        if len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

        Z = img.reshape((-1, 3)).astype(np.float32)

        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
        _, labels, centers = cv2.kmeans(Z, k, None, criteria, 3, cv2.KMEANS_PP_CENTERS)
        centers = np.uint8(centers)
        res = centers[labels.flatten()]
        out = res.reshape(img.shape)
        return out

    @staticmethod
    def seg_meanshift(image: np.ndarray, **params) -> np.ndarray:
        """
        Mean Shift segmentation (OpenCV pyrMeanShiftFiltering).
        Output: smoothed + segmented appearance.
        """
        if image is None or image.size == 0:
            return image

        sp = int(params.get("sp", 10))
        sr = int(params.get("sr", 20))
        sp = max(1, min(80, sp))
        sr = max(1, min(120, sr))

        img = image.copy()
        if len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

        out = cv2.pyrMeanShiftFiltering(img, sp=sp, sr=sr)
        return out


FILTER_MAP = {
    "seg_watershed_manual": SegmentationFilters.seg_watershed_manual,
    "seg_watershed_opencv": SegmentationFilters.seg_watershed_opencv,
    "seg_kmeans": SegmentationFilters.seg_kmeans,
    "seg_meanshift": SegmentationFilters.seg_meanshift,
}
