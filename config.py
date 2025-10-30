"""
تنظیمات و ثابت‌های برنامه
Application Configuration and Constants
"""

# =============== تنظیمات UI ===============
WINDOW_TITLE = "پردازش تصویر و فوتوگرامتری - Image Processing & Photogrammetry"
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900

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


# =============== پالت رنگی (Dark Theme) ===============
class Colors:
    """رنگ‌های برنامه"""

    # پس‌زمینه
    BACKGROUND = "#1e1e1e"
    PANEL = "#2d2d2d"
    WIDGET = "#3d3d3d"
    BORDER = "#444444"

    # اصلی
    PRIMARY = "#0d7377"
    PRIMARY_LIGHT = "#14a085"
    PRIMARY_DARK = "#0a5f62"

    # متن
    TEXT = "#ffffff"
    TEXT_SECONDARY = "#b0b0b0"

    # وضعیت
    SUCCESS = "#4CAF50"
    WARNING = "#ff9800"
    ERROR = "#ff0000"
    INFO = "#2196F3"

    # ویوئر تصویر
    IMAGE_VIEWER_BG = "#2b2b2b"
    IMAGE_VIEWER_BORDER = "#444444"


# =============== تنظیمات استایل ===============
class Fonts:
    """فونت‌های برنامه"""

    FAMILY = "'Segoe UI', Tahoma, Arial"
    SIZE_BASE = 12
    SIZE_HEADER = 18
    SIZE_BUTTON = 12


# =============== تنظیمات Threading ===============
PROCESSING_TIMEOUT = 30  # ثانیه
THREAD_PRIORITY = "Normal"

# =============== لیست فیلترها ===============
FILTER_CATEGORIES = {
    "basic": "فیلترهای پایه",
    "edge": "لبه‌یابی",
    "photo": "فوتوگرامتری",
    "creative": "خلاقانه",
    "color": "رنگی",
}
