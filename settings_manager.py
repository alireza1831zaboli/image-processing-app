"""
مدیریت تنظیمات
Settings Manager
"""

import json
import os
from pathlib import Path
from typing import Any, Dict


class SettingsManager:
    """کلاس مدیریت تنظیمات برنامه"""

    # مسیر فایل تنظیمات
    SETTINGS_FILE = "app_settings.json"

    # تنظیمات پیشفرض
    DEFAULT_SETTINGS = {
        # ظاهر
        "language": "fa",  # fa یا en
        "theme": "dark",  # dark یا light

        # تجربه کاربری
        "zoom_speed": "normal",  # slow, normal, fast
        "show_hints": True,
        "confirm_exit": True,

        # فایل‌ها
        "save_quality": "high",  # low, medium, high, maximum
        "default_format": "PNG",  # PNG, JPEG, BMP
        "last_directory": "",  # آخرین مسیر باز/ذخیره
    }

    def __init__(self):
        """سازنده"""
        self.settings = self.DEFAULT_SETTINGS.copy()
        self.load()

    def get(self, key: str, default: Any = None) -> Any:
        """دریافت یک تنظیم"""
        return self.settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """تنظیم یک مقدار"""
        self.settings[key] = value

    def get_all(self) -> Dict[str, Any]:
        """دریافت همه تنظیمات"""
        return self.settings.copy()

    def update(self, new_settings: Dict[str, Any]) -> None:
        """به‌روزرسانی چند تنظیم"""
        self.settings.update(new_settings)

    def reset(self) -> None:
        """بازنشانی به تنظیمات پیشفرض"""
        self.settings = self.DEFAULT_SETTINGS.copy()

    def load(self) -> bool:
        """بارگذاری تنظیمات از فایل"""
        try:
            if os.path.exists(self.SETTINGS_FILE):
                with open(self.SETTINGS_FILE, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    # ادغام با پیشفرض (برای کلیدهای جدید)
                    self.settings = {**self.DEFAULT_SETTINGS, **loaded}
                return True
        except Exception as e:
            print(f"خطا در بارگذاری تنظیمات: {e}")
        return False

    def save(self) -> bool:
        """ذخیره تنظیمات در فایل"""
        try:
            with open(self.SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"خطا در ذخیره تنظیمات: {e}")
            return False

    # ========== متدهای کمکی ==========

    def get_zoom_factor(self) -> float:
        """دریافت ضریب zoom بر اساس سرعت"""
        speed = self.get("zoom_speed", "normal")
        factors = {"slow": 1.1, "normal": 1.2, "fast": 1.5}
        return factors.get(speed, 1.2)

    def get_quality_value(self) -> int:
        """دریافت مقدار کیفیت (0-100)"""
        quality = self.get("save_quality", "high")
        values = {"low": 50, "medium": 75, "high": 90, "maximum": 100}
        return values.get(quality, 90)

    def is_rtl(self) -> bool:
        """آیا زبان راست‌به‌چپ است؟"""
        return self.get("language", "fa") == "fa"


# نمونه سینگلتون
_settings_instance = None


def get_settings() -> SettingsManager:
    """دریافت نمونه سینگلتون تنظیمات"""
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = SettingsManager()
    return _settings_instance
