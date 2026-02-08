"""
سیستم ترجمه - دیکشنری فارسی/انگلیسی
Translation System
"""


class Translations:
    """کلاس مدیریت ترجمه‌ها"""

    # دیکشنری کامل ترجمه‌ها
    TEXTS = {
        # عنوان برنامه
        "app_title": {
            "fa": "پردازش تصویر و فتوگرامتری",
            "en": "Image Processing & Photogrammetry",
        },
        # منوها
        "file_menu": {"fa": "فایل", "en": "File"},
        "edit_menu": {"fa": "ویرایش", "en": "Edit"},
        "view_menu": {"fa": "نمایش", "en": "View"},
        "tools_menu": {"fa": "ابزار", "en": "Tools"},
        "help_menu": {"fa": "راهنما", "en": "Help"},
        # دکمه‌های اصلی
        "load_image": {"fa": "بارگذاری تصویر", "en": "Load Image"},
        "save_image": {"fa": "ذخیره تصویر", "en": "Save Image"},
        "reset": {"fa": "بازنشانی", "en": "Reset"},
        "settings": {"fa": "تنظیمات", "en": "Settings"},
        # پنل کنترل
        "control_panel": {"fa": "پنل کنترل", "en": "Control Panel"},
        "filter_selection": {"fa": "انتخاب فیلتر", "en": "Filter Selection"},
        "operations": {"fa": "عملیات", "en": "Operations"},
        "zoom_pan": {"fa": "زوم و حرکت", "en": "Zoom & Pan"},
        # تب‌ها
        "image_view": {"fa": "🖼️ نمایش تصویر", "en": "🖼️ Image View"},
        "histogram_view": {"fa": "📊 نمایش هیستوگرام", "en": "📊 Histogram View"},
        # تصاویر
        "original_image": {"fa": "تصویر اصلی", "en": "Original Image"},
        "processed_image": {"fa": "تصویر پردازش شده", "en": "Processed Image"},
        "original_histogram": {
            "fa": "هیستوگرام تصویر اصلی",
            "en": "Original Image Histogram",
        },
        "processed_histogram": {
            "fa": "هیستوگرام تصویر پردازش شده",
            "en": "Processed Image Histogram",
        },
        # دسته‌بندی فیلترها
        "category_base": {"fa": "پایه", "en": "Base"},
        "category_enhancement": {"fa": "لبه‌یابی", "en": "Enhancement"},
        "category_photogrammetry": {"fa": "فتوگرامتری", "en": "Photogrammetry"},
        "category_advanced": {"fa": "خلاقانه", "en": "Creative"},
        "category_transformation": {"fa": "تبدیل هندسی", "en": "Transformation"},
        "category_point_detection": {"fa": "تشخیص نقاط", "en": "Point Detection"},
        # فیلترهای Transformation - جدید! ✅
        "filter_transform_direct": {"fa": "نقشه‌برداری مستقیم", "en": "Direct Map"},
        "filter_transform_inverse_nn": {
            "fa": "نقشه‌برداری معکوس (NN)",
            "en": "Inverse Map (NN)",
        },
        "filter_transform_inverse_bilinear": {
            "fa": "نقشه‌برداری معکوس (دوخطی)",
            "en": "Inverse Map (Bilinear)",
        },
        "filter_transform_inverse_bicubic": {
            "fa": "نقشه‌برداری معکوس (دومکعبی)",
            "en": "Inverse Map (Bicubic)",
        },
        # فیلترها
        "filter_original": {"fa": "اصلی", "en": "Original"},
        "filter_grayscale": {"fa": "خاکستری", "en": "Grayscale"},
        "filter_blur": {"fa": "محو کردن", "en": "Blur"},
        "filter_sharpen": {"fa": "تیز کردن", "en": "Sharpen"},
        "filter_bilateral": {"fa": "فیلتر دو سویه", "en": "Bilateral Filter"},
        "filter_median": {"fa": "فیلتر میانه", "en": "Median Filter"},
        "filter_histogram_eq": {"fa": "هیستوگرام", "en": "Histogram Equalization"},
        "filter_clahe": {"fa": "CLAHE", "en": "CLAHE"},
        "filter_canny": {"fa": "Canny", "en": "Canny Edge"},
        "filter_sobel": {"fa": "Sobel", "en": "Sobel"},
        "filter_laplacian": {"fa": "Laplacian", "en": "Laplacian"},
        "filter_scharr": {"fa": "Scharr", "en": "Scharr"},
        "filter_contrast": {"fa": "کشیدگی کنتراست", "en": "Contrast Stretch"},
        "filter_gamma": {"fa": "تصحیح گاما", "en": "Gamma Correction"},
        "filter_threshold": {"fa": "آستانه‌گذاری", "en": "Threshold"},
        "filter_otsu": {"fa": "Otsu", "en": "Otsu"},
        "filter_morphology": {"fa": "مورفولوژی", "en": "Morphology"},
        "filter_clay": {"fa": "افکت گلی", "en": "Clay Effect"},
        "filter_negative": {"fa": "نگاتیو", "en": "Negative"},
        "filter_sepia": {"fa": "سپیا", "en": "Sepia"},
        "filter_emboss": {"fa": "برجسته", "en": "Emboss"},
        "filter_cartoon": {"fa": "کارتونی", "en": "Cartoon"},
        "filter_pencil": {"fa": "طرح مداد", "en": "Pencil Sketch"},
        "filter_watercolor": {"fa": "آبرنگ", "en": "Watercolor"},
        "filter_hsv": {"fa": "HSV", "en": "HSV"},
        "filter_lab": {"fa": "LAB", "en": "LAB"},
        "filter_hue": {"fa": "تغییر رنگ", "en": "Hue Shift"},
        "filter_saturation": {"fa": "اشباع", "en": "Saturation"},
        "filter_brightness": {"fa": "روشنایی", "en": "Brightness"},
        "filter_temperature": {"fa": "دما", "en": "Temperature"},

        # Point Detection filters (Project #3)
        "filter_moravec_corner": {"fa": "Moravec", "en": "Moravec"},
        "filter_haralick_corner": {"fa": "Haralick", "en": "Haralick"},
        "filter_harris_corner": {"fa": "Harris", "en": "Harris"},
        # پارامترها
        "blur_amount": {"fa": "اندازه Blur", "en": "Blur Amount"},
        "clahe_value": {"fa": "CLAHE", "en": "CLAHE"},
        "settings_label": {"fa": "تنظیمات", "en": "Settings"},
        # دکمه‌های Zoom
        "zoom_in": {"fa": "بزرگ‌نمایی", "en": "Zoom In"},
        "zoom_out": {"fa": "کوچک‌نمایی", "en": "Zoom Out"},
        "zoom_reset": {"fa": "بازنشانی", "en": "Reset Zoom"},
        # Status Bar
        "status_filter": {"fa": "فیلتر", "en": "Filter"},
        "status_file": {"fa": "فایل", "en": "File"},
        "status_dimensions": {"fa": "ابعاد", "en": "Dimensions"},
        "status_coords": {"fa": "مختصات", "en": "Coordinates"},
        # پیام‌ها
        "msg_loading": {"fa": "در حال بارگذاری", "en": "Loading"},
        "msg_processing": {"fa": "در حال پردازش", "en": "Processing"},
        "msg_success": {"fa": "موفقیت", "en": "Success"},
        "msg_error": {"fa": "خطا", "en": "Error"},
        "msg_warning": {"fa": "هشدار", "en": "Warning"},
        "msg_image_loaded": {
            "fa": "تصویر با موفقیت بارگذاری شد",
            "en": "Image loaded successfully",
        },
        "msg_image_saved": {
            "fa": "تصویر با موفقیت ذخیره شد",
            "en": "Image saved successfully",
        },
        "msg_filter_applied": {"fa": "فیلتر اعمال شد", "en": "Filter applied"},
        "msg_no_image": {"fa": "تصویری بارگذاری نشده", "en": "No image loaded"},
        "msg_reset": {"fa": "تصویر بازنشانی شد", "en": "Image reset"},
        # تنظیمات
        "settings_title": {"fa": "تنظیمات", "en": "Settings"},
        "settings_language": {"fa": "زبان", "en": "Language"},
        "settings_theme": {"fa": "پوسته", "en": "Theme"},
        "settings_appearance": {"fa": "ظاهری", "en": "Appearance"},
        "settings_performance": {"fa": "عملکرد", "en": "Performance"},
        "settings_files": {"fa": "فایل‌ها", "en": "Files"},
        "settings_advanced": {"fa": "پیشرفته", "en": "Advanced"},
        # زبان‌ها
        "lang_persian": {"fa": "فارسی", "en": "Persian"},
        "lang_english": {"fa": "انگلیسی", "en": "English"},
        # پوسته
        "theme_dark": {"fa": "تیره", "en": "Dark"},
        "theme_light": {"fa": "روشن", "en": "Light"},
        "theme_auto": {"fa": "خودکار", "en": "Auto"},
        # کیفیت
        "quality_low": {"fa": "کم", "en": "Low"},
        "quality_medium": {"fa": "متوسط", "en": "Medium"},
        "quality_high": {"fa": "بالا", "en": "High"},
        "quality_maximum": {"fa": "حداکثر", "en": "Maximum"},
        # سرعت
        "speed_slow": {"fa": "کند", "en": "Slow"},
        "speed_normal": {"fa": "متوسط", "en": "Normal"},
        "speed_fast": {"fa": "سریع", "en": "Fast"},
        # دکمه‌های Dialog
        "btn_apply": {"fa": "اعمال", "en": "Apply"},
        "btn_ok": {"fa": "تایید", "en": "OK"},
        "btn_cancel": {"fa": "لغو", "en": "Cancel"},
        "btn_reset": {"fa": "بازنشانی", "en": "Reset"},
        "btn_close": {"fa": "بستن", "en": "Close"},
        # تنظیمات جزئی
        "save_quality": {"fa": "کیفیت ذخیره", "en": "Save Quality"},
        "default_format": {"fa": "فرمت پیشفرض", "en": "Default Format"},
        "zoom_speed": {"fa": "سرعت Zoom", "en": "Zoom Speed"},
        "show_grid": {"fa": "نمایش Grid", "en": "Show Grid"},
        "grid_size": {"fa": "اندازه Grid", "en": "Grid Size"},
        "auto_save": {"fa": "ذخیره خودکار", "en": "Auto Save"},
        "auto_save_interval": {"fa": "فاصله ذخیره", "en": "Save Interval"},
        "history_size": {"fa": "تعداد Undo/Redo", "en": "History Size"},
        "show_hints": {"fa": "نمایش راهنما", "en": "Show Hints"},
        "confirm_exit": {"fa": "تایید خروج", "en": "Confirm Exit"},
        # واحدها
        "unit_minutes": {"fa": "دقیقه", "en": "minutes"},
        "unit_pixels": {"fa": "پیکسل", "en": "pixels"},
        "unit_steps": {"fa": "مرحله", "en": "steps"},
        # راهنمای کلیدها
        "hint_mousewheel": {"fa": "Mouse Wheel: Zoom", "en": "Mouse Wheel: Zoom"},
        "hint_clickdrag": {"fa": "Click + Drag: حرکت", "en": "Click + Drag: Pan"},
    }

    @classmethod
    def get(cls, key: str, lang: str = "fa") -> str:
        """دریافت ترجمه یک کلید"""
        if key in cls.TEXTS:
            return cls.TEXTS[key].get(lang, cls.TEXTS[key].get("fa", key))
        return key

    @classmethod
    def get_filter_name(cls, filter_key: str, lang: str = "fa") -> str:
        """دریافت نام فیلتر"""
        key = f"filter_{filter_key}"
        return cls.get(key, lang)
