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

# پالت‌های آماده (Dark/Light) برای حفظ زیبایی در هر دو حالت
_PALETTE_DARK = {
    # Backgrounds
    "BACKGROUND": "#1a1e23",
    "PANEL": "#22272e",
    "WIDGET": "#2d333b",
    "BORDER": "#444c56",

    # Accent (Teal/Cyan)
    "PRIMARY": "#0f6f73",
    "PRIMARY_LIGHT": "#148489",
    "PRIMARY_DARK": "#0b5b5e",
    "PRIMARY_HOVER": "#0078D4",

    # Text
    "TEXT": "#e6edf3",
    "TEXT_SECONDARY": "#9198a1",
    "TEXT_MUTED": "#656d76",

    # Status
    "SUCCESS": "#3fb950",
    "WARNING": "#d29922",
    "ERROR": "#ff5555",
    "INFO": "#58a6ff",

    # Image viewer
    "IMAGE_VIEWER_BG": "#1a1e23",
    "IMAGE_VIEWER_BORDER": "#444c56",

    # Hover
    "HOVER": "#373e47",
}

_PALETTE_LIGHT = {
    # Backgrounds
    "BACKGROUND": "#f1f3f5",
    "PANEL": "#ffffff",
    "WIDGET": "#f3f4f6",
    "BORDER": "#d0d7de",

    # Accent (Teal/Cyan) – هماهنگ با تم تیره
    "PRIMARY": "#0f6f73",
    "PRIMARY_LIGHT": "#148489",
    "PRIMARY_DARK": "#0b5b5e",
    "PRIMARY_HOVER": "#116a6e",

    # Text
    "TEXT": "#24292f",
    "TEXT_SECONDARY": "#57606a",
    "TEXT_MUTED": "#6e7781",

    # Status
    "SUCCESS": "#1a7f37",
    "WARNING": "#9a6700",
    "ERROR": "#cf222e",
    "INFO": "#0969da",

    # Image viewer
    "IMAGE_VIEWER_BG": "#f6f8fa",
    "IMAGE_VIEWER_BORDER": "#d0d7de",

    # Hover
    "HOVER": "#eaeef2",
}


class Colors:
    """رنگ‌های فعال برنامه (با امکان سوئیچ تم در لحظه)"""

    # مقدار پیش‌فرض
    BACKGROUND = _PALETTE_DARK["BACKGROUND"]
    PANEL = _PALETTE_DARK["PANEL"]
    WIDGET = _PALETTE_DARK["WIDGET"]
    BORDER = _PALETTE_DARK["BORDER"]

    PRIMARY = _PALETTE_DARK["PRIMARY"]
    PRIMARY_LIGHT = _PALETTE_DARK["PRIMARY_LIGHT"]
    PRIMARY_DARK = _PALETTE_DARK["PRIMARY_DARK"]
    PRIMARY_HOVER = _PALETTE_DARK["PRIMARY_HOVER"]

    TEXT = _PALETTE_DARK["TEXT"]
    TEXT_SECONDARY = _PALETTE_DARK["TEXT_SECONDARY"]
    TEXT_MUTED = _PALETTE_DARK["TEXT_MUTED"]

    SUCCESS = _PALETTE_DARK["SUCCESS"]
    WARNING = _PALETTE_DARK["WARNING"]
    ERROR = _PALETTE_DARK["ERROR"]
    INFO = _PALETTE_DARK["INFO"]

    IMAGE_VIEWER_BG = _PALETTE_DARK["IMAGE_VIEWER_BG"]
    IMAGE_VIEWER_BORDER = _PALETTE_DARK["IMAGE_VIEWER_BORDER"]

    HOVER = _PALETTE_DARK["HOVER"]


def set_theme(theme: str) -> str:
    """اعمال تم (dark/light) روی رنگ‌های config در لحظه"""
    theme = (theme or "dark").lower()
    palette = _PALETTE_LIGHT if theme == "light" else _PALETTE_DARK

    for k, v in palette.items():
        setattr(Colors, k, v)

    return "light" if theme == "light" else "dark"


# =============== تنظیمات استایل ===============

class Fonts:
    """فونتهای برنامه - متعادل"""

    FAMILY = "Segoe UI, Inter, Arial"
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