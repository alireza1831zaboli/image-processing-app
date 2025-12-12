"""
تنظیمات و ثابتهای برنامه - نسخه متعادل و Responsive
Application Configuration - Balanced & Responsive
"""

# =============== تنظیمات UI ===============
WINDOW_TITLE = "Image Processing & Photogrammetry"
WINDOW_WIDTH = 1350
WINDOW_HEIGHT = 800
WINDOW_MIN_WIDTH = 1000
WINDOW_MIN_HEIGHT = 700  # ✅ افزایش از 650 به 700

# =============== تنظیمات پنل کنترل ===============
CONTROL_PANEL_WIDTH = 270
CONTROL_PANEL_MIN_WIDTH = 270  # ✅ جدید
CONSOLE_HEIGHT = 110

# ✅ حداقل ارتفاع GroupBox ها
GROUP_BOX_MIN_HEIGHTS = {
    "filters": 120,
    "parameters": 80,
    "apply": 90,
    "operations": 110,
    "zoom": 130,
}

# =============== تنظیمات تصویر ===============
SUPPORTED_FORMATS = "Images (*.png *.jpg *.jpeg *.bmp *.tiff *.tif)"
MIN_IMAGE_SIZE = (100, 100)
MAX_IMAGE_SIZE = (8000, 8000)

# =============== تنظیمات Zoom ===============
ZOOM_MIN = 0.1
ZOOM_MAX = 10.0
ZOOM_STEP = 0.1
ZOOM_WHEEL_FACTOR = 1.15

# =============== تنظیمات Pan ===============
PAN_ENABLED = True
PAN_CURSOR_OPEN = "hand"
PAN_CURSOR_CLOSED = "closedhand"


# =============== پالت رنگی ===============
class Colors:
    """رنگهای برنامه - تم Teal مدرن"""

    # پسزمینه
    BACKGROUND = "#1a1e23"
    PANEL = "#22272e"
    WIDGET = "#2d333b"
    BORDER = "#444c56"

    # اصلی - Teal/Cyan
    PRIMARY = "#0d7377"
    PRIMARY_LIGHT = "#14a085"
    PRIMARY_DARK = "#0a5f62"

    # متن
    TEXT = "#e6edf3"
    TEXT_SECONDARY = "#9198a1"
    TEXT_MUTED = "#656d76"

    # وضعیت
    SUCCESS = "#3fb950"
    WARNING = "#d29922"
    ERROR = "#ff5555"
    INFO = "#58a6ff"

    # ویوئر تصویر
    IMAGE_VIEWER_BG = "#1a1e23"
    IMAGE_VIEWER_BORDER = "#444c56"

    # Hover
    HOVER = "#373e47"


# =============== تنظیمات استایل ===============
class Fonts:
    """فونتهای برنامه - متعادل"""

    FAMILY = "'Segoe UI', 'Inter', system-ui, -apple-system, sans-serif"
    SIZE_BASE = 11
    SIZE_SMALL = 10
    SIZE_HEADER = 12
    SIZE_TITLE = 14
    SIZE_BUTTON = 11


# =============== تنظیمات Layout ===============
class Layout:
    """تنظیمات Layout متعادل"""

    SPACING_SMALL = 3
    SPACING_MEDIUM = 6
    SPACING_LARGE = 8

    PADDING_SMALL = 5
    PADDING_MEDIUM = 8
    PADDING_LARGE = 10

    RADIUS_SMALL = 4
    RADIUS_MEDIUM = 5
    RADIUS_LARGE = 6

    CONTROL_HEIGHT = 28
    BUTTON_HEIGHT = 30


# =============== تنظیمات Threading ===============
PROCESSING_TIMEOUT = 30
THREAD_PRIORITY = "Normal"
