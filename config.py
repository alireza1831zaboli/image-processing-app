"""
تنظیمات و ثابتهای برنامه - نسخه بهینه شده
Application Configuration and Constants - Optimized Version
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

# =============== پالت رنگی (Refined Teal Theme) ===============
class Colors:
    """رنگهای برنامه - تم Teal مدرن"""
    
    # پسزمینه
    BACKGROUND = "#1a1e23"          # خیلی تیره
    PANEL = "#22272e"               # تیره
    WIDGET = "#2d333b"              # ویجت
    BORDER = "#444c56"              # بوردر
    
    # اصلی - Teal/Cyan (رنگ قبلی بهتر شده)
    PRIMARY = "#0d7377"             # Teal اصلی
    PRIMARY_LIGHT = "#14a085"       # Teal روشن
    PRIMARY_DARK = "#0a5f62"        # Teal تیره
    
    # متن
    TEXT = "#e6edf3"                # سفید نرم
    TEXT_SECONDARY = "#9198a1"      # خاکستری
    TEXT_MUTED = "#656d76"          # خاکستری تیره
    
    # وضعیت
    SUCCESS = "#3fb950"             # سبز
    WARNING = "#d29922"             # نارنجی
    ERROR = "#ff5555"               # قرمز
    INFO = "#58a6ff"                # آبی
    
    # ویوئر تصویر
    IMAGE_VIEWER_BG = "#1a1e23"
    IMAGE_VIEWER_BORDER = "#444c56"
    
    # Hover
    HOVER = "#373e47"

# =============== تنظیمات استایل ===============
class Fonts:
    """فونتهای برنامه"""
    FAMILY = "'Segoe UI', 'Inter', system-ui, -apple-system, sans-serif"
    SIZE_BASE = 12
    SIZE_SMALL = 11
    SIZE_HEADER = 14
    SIZE_TITLE = 16
    SIZE_BUTTON = 12

# =============== تنظیمات Layout ===============
class Layout:
    """تنظیمات Layout بهینه"""
    SPACING_SMALL = 4
    SPACING_MEDIUM = 8
    SPACING_LARGE = 12
    PADDING_SMALL = 6
    PADDING_MEDIUM = 10
    PADDING_LARGE = 14
    RADIUS_SMALL = 5
    RADIUS_MEDIUM = 6
    RADIUS_LARGE = 8
    CONTROL_HEIGHT = 32
    BUTTON_HEIGHT = 34

# =============== تنظیمات Threading ===============
PROCESSING_TIMEOUT = 30
THREAD_PRIORITY = "Normal"

# =============== لیست فیلترها ===============
FILTER_CATEGORIES = {
    "basic": "فیلترهای پایه",
    "edge": "لبهیابی",
    "photo": "فوتوگرامتری",
    "creative": "خلاقانه",
    "color": "رنگی",
}
