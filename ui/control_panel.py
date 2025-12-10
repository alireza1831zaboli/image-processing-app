"""
پنل کنترل ساده با پشتیبانی تنظیمات
Simple Control Panel with Settings Support
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QComboBox,
    QLabel,
    QSlider,
    QSpinBox,
    QDoubleSpinBox,
    QGroupBox,
    QScrollArea,
)
from PySide6.QtCore import Qt, Signal
import config

try:
    from translations import Translations
    from settings_manager import get_settings

    USE_TRANSLATIONS = True
except ImportError:
    USE_TRANSLATIONS = False

    class Translations:
        @staticmethod
        def get(key, lang="fa"):
            return key


class ControlPanel(QWidget):
    """پنل کنترل"""

    filter_changed = Signal(str, dict)
    load_clicked = Signal()
    save_clicked = Signal()
    reset_clicked = Signal()
    settings_clicked = Signal()
    zoom_in_clicked = Signal()
    zoom_out_clicked = Signal()
    zoom_reset_clicked = Signal()

    def __init__(self):
        super().__init__()

        if USE_TRANSLATIONS:
            self.settings = get_settings()
            self.current_lang = self.settings.get("language", "fa")
        else:
            self.current_lang = "fa"

        self.setup_ui()

    def setup_ui(self):
        """ساخت UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # عنوان
        if USE_TRANSLATIONS:
            title_text = Translations.get("control_panel", self.current_lang)
        else:
            title_text = "پنل کنترل"

        title = QLabel(title_text)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            f"""
            QLabel {{
                color: {config.Colors.PRIMARY};
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
                background-color: {config.Colors.WIDGET};
                border-radius: 8px;
            }}
        """
        )
        main_layout.addWidget(title)

        # Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(10)

        # گروه انتخاب فیلتر
        self.filter_group = self.create_filter_group()
        scroll_layout.addWidget(self.filter_group)

        # گروه تنظیمات فیلتر
        self.params_group = self.create_params_group()
        scroll_layout.addWidget(self.params_group)

        # گروه عملیات
        self.operations_group = self.create_operations_group()
        scroll_layout.addWidget(self.operations_group)

        # گروه Zoom
        self.zoom_group = self.create_zoom_group()
        scroll_layout.addWidget(self.zoom_group)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        # راهنما
        if USE_TRANSLATIONS:
            hint_text = Translations.get("hint_mousewheel", self.current_lang)
        else:
            hint_text = "Mouse Wheel: Zoom"

        self.hint_label = QLabel(hint_text)
        self.hint_label.setWordWrap(True)
        self.hint_label.setStyleSheet(
            f"""
            QLabel {{
                color: {config.Colors.TEXT_SECONDARY};
                font-size: 10px;
                padding: 5px;
                background-color: {config.Colors.BACKGROUND};
                border-radius: 4px;
            }}
        """
        )
        main_layout.addWidget(self.hint_label)

    def create_filter_group(self):
        """گروه انتخاب فیلتر"""
        if USE_TRANSLATIONS:
            group_title = "📁 " + Translations.get(
                "filter_selection", self.current_lang
            )
        else:
            group_title = "📁 انتخاب فیلتر"

        group = QGroupBox(group_title)
        layout = QVBoxLayout()

        # دسته‌بندی‌ها
        self.category_combo = QComboBox()
        if USE_TRANSLATIONS:
            self.category_combo.addItem(
                "🎨 " + Translations.get("category_base", self.current_lang), "base"
            )
            self.category_combo.addItem(
                "✨ " + Translations.get("category_enhancement", self.current_lang),
                "enhancement",
            )
            self.category_combo.addItem(
                "📷 " + Translations.get("category_photogrammetry", self.current_lang),
                "photogrammetry",
            )
            self.category_combo.addItem(
                "🎭 " + Translations.get("category_advanced", self.current_lang),
                "advanced",
            )
        else:
            self.category_combo.addItem("🎨 پایه", "base")
            self.category_combo.addItem("✨ لبه‌یابی", "enhancement")
            self.category_combo.addItem("📷 فتوگرامتری", "photogrammetry")
            self.category_combo.addItem("🎭 خلاقانه", "advanced")

        self.category_combo.currentIndexChanged.connect(self.on_category_changed)
        layout.addWidget(self.category_combo)

        # فیلترها
        self.filter_combo = QComboBox()
        self.filter_combo.blockSignals(True)  # موقتاً signal ها رو غیرفعال کن
        self.filter_combo.currentIndexChanged.connect(self.on_filter_changed)
        layout.addWidget(self.filter_combo)

        group.setLayout(layout)
        self.populate_filters()
        self.filter_combo.blockSignals(False)  # signal ها رو دوباره فعال کن
        return group

        # self.filter_combo = QComboBox()
        # self.filter_combo.currentIndexChanged.connect(self.on_filter_changed)
        # layout.addWidget(self.filter_combo)

        # group.setLayout(layout)
        # self.populate_filters()
        # return group

    def create_params_group(self):
        """گروه تنظیمات"""
        if USE_TRANSLATIONS:
            group_title = "⚙️ " + Translations.get("settings_label", self.current_lang)
        else:
            group_title = "⚙️ تنظیمات"

        group = QGroupBox(group_title)
        layout = QVBoxLayout()

        # Blur Amount
        blur_layout = QHBoxLayout()
        if USE_TRANSLATIONS:
            blur_label_text = Translations.get("blur_amount", self.current_lang) + ":"
        else:
            blur_label_text = "اندازه Blur:"

        blur_label = QLabel(blur_label_text)
        self.blur_slider = QSlider(Qt.Horizontal)
        self.blur_slider.setRange(1, 30)
        self.blur_slider.setValue(15)
        self.blur_slider.valueChanged.connect(self.on_params_changed)
        self.blur_value_label = QLabel("15")
        self.blur_value_label.setFixedWidth(30)
        blur_layout.addWidget(blur_label)
        blur_layout.addWidget(self.blur_slider)
        blur_layout.addWidget(self.blur_value_label)
        layout.addLayout(blur_layout)

        self.blur_slider.valueChanged.connect(
            lambda v: self.blur_value_label.setText(str(v))
        )

        # CLAHE
        clahe_layout = QHBoxLayout()
        if USE_TRANSLATIONS:
            clahe_label_text = Translations.get("clahe_value", self.current_lang) + ":"
        else:
            clahe_label_text = "CLAHE:"

        clahe_label = QLabel(clahe_label_text)
        self.clahe_spin = QDoubleSpinBox()
        self.clahe_spin.setRange(1.0, 5.0)
        self.clahe_spin.setSingleStep(0.1)
        self.clahe_spin.setValue(2.0)
        self.clahe_spin.valueChanged.connect(self.on_params_changed)
        clahe_layout.addWidget(clahe_label)
        clahe_layout.addWidget(self.clahe_spin)
        layout.addLayout(clahe_layout)

        group.setLayout(layout)
        return group

    def create_operations_group(self):
        """گروه عملیات"""
        if USE_TRANSLATIONS:
            group_title = "🔧 " + Translations.get("operations", self.current_lang)
        else:
            group_title = "🔧 عملیات"

        group = QGroupBox(group_title)
        layout = QVBoxLayout()
        layout.setSpacing(8)

        # بارگذاری
        if USE_TRANSLATIONS:
            load_text = "📁 " + Translations.get("load_image", self.current_lang)
        else:
            load_text = "📁 بارگذاری تصویر"

        self.load_btn = QPushButton(load_text)
        self.load_btn.clicked.connect(self.load_clicked.emit)
        layout.addWidget(self.load_btn)

        # ذخیره
        if USE_TRANSLATIONS:
            save_text = "💾 " + Translations.get("save_image", self.current_lang)
        else:
            save_text = "💾 ذخیره تصویر"

        self.save_btn = QPushButton(save_text)
        self.save_btn.clicked.connect(self.save_clicked.emit)
        layout.addWidget(self.save_btn)

        # تنظیمات
        if USE_TRANSLATIONS:
            settings_text = "⚙️ " + Translations.get("settings", self.current_lang)
        else:
            settings_text = "⚙️ تنظیمات"

        self.settings_btn = QPushButton(settings_text)
        self.settings_btn.clicked.connect(self.settings_clicked.emit)
        layout.addWidget(self.settings_btn)

        group.setLayout(layout)
        return group

    def create_zoom_group(self):
        """گروه Zoom"""
        if USE_TRANSLATIONS:
            group_title = "🔍 " + Translations.get("zoom_pan", self.current_lang)
        else:
            group_title = "🔍 زوم و حرکت"

        group = QGroupBox(group_title)
        layout = QHBoxLayout()

        # Zoom In
        if USE_TRANSLATIONS:
            zoom_in_text = "🔍 " + Translations.get("zoom_in", self.current_lang)
        else:
            zoom_in_text = "🔍 بزرگ‌نمایی"

        self.zoom_in_btn = QPushButton(zoom_in_text)
        self.zoom_in_btn.clicked.connect(self.zoom_in_clicked.emit)
        layout.addWidget(self.zoom_in_btn)

        # Zoom Out
        if USE_TRANSLATIONS:
            zoom_out_text = "🔎 " + Translations.get("zoom_out", self.current_lang)
        else:
            zoom_out_text = "🔎 کوچک‌نمایی"

        self.zoom_out_btn = QPushButton(zoom_out_text)
        self.zoom_out_btn.clicked.connect(self.zoom_out_clicked.emit)
        layout.addWidget(self.zoom_out_btn)

        # Reset
        reset_layout = QVBoxLayout()

        if USE_TRANSLATIONS:
            zoom_reset_text = "🔄 " + Translations.get("zoom_reset", self.current_lang)
            reset_text = "↺ " + Translations.get("reset", self.current_lang)
        else:
            zoom_reset_text = "🔄 بازنشانی"
            reset_text = "↺ بازنشانی"

        self.zoom_reset_btn = QPushButton(zoom_reset_text)
        self.zoom_reset_btn.clicked.connect(self.zoom_reset_clicked.emit)
        reset_layout.addWidget(self.zoom_reset_btn)

        self.reset_btn = QPushButton(reset_text)
        self.reset_btn.clicked.connect(self.reset_clicked.emit)
        reset_layout.addWidget(self.reset_btn)

        group_layout = QVBoxLayout()
        group_layout.addLayout(layout)
        group_layout.addLayout(reset_layout)
        group.setLayout(group_layout)
        return group

    def populate_filters(self):
        """پر کردن لیست فیلترها"""
        self.filters_data = {
            "base": [
                ("original", "filter_original"),
                ("grayscale", "filter_grayscale"),
                ("blur", "filter_blur"),
                ("sharpen", "filter_sharpen"),
            ],
            "enhancement": [
                ("bilateral", "filter_bilateral"),
                ("median", "filter_median"),
                ("histogram_equalization", "filter_histogram_eq"),
                ("clahe", "filter_clahe"),
                ("canny", "filter_canny"),
                ("sobel", "filter_sobel"),
                ("laplacian", "filter_laplacian"),
                ("scharr", "filter_scharr"),
            ],
            "photogrammetry": [
                ("contrast_stretch", "filter_contrast"),
                ("gamma", "filter_gamma"),
                ("threshold", "filter_threshold"),
                ("otsu", "filter_otsu"),
                ("morphology", "filter_morphology"),
            ],
            "advanced": [
                ("clay", "filter_clay"),
                ("negative", "filter_negative"),
                ("sepia", "filter_sepia"),
                ("emboss", "filter_emboss"),
                ("cartoon", "filter_cartoon"),
                ("pencil_sketch", "filter_pencil"),
                ("watercolor", "filter_watercolor"),
                ("hsv", "filter_hsv"),
                ("lab", "filter_lab"),
                ("hue_shift", "filter_hue"),
                ("saturation", "filter_saturation"),
                ("brightness", "filter_brightness"),
                ("temperature", "filter_temperature"),
            ],
        }
        self.on_category_changed(0)

    def on_category_changed(self, index):
        """تغییر دسته‌بندی"""
        category = self.category_combo.currentData()
        self.filter_combo.clear()

        if category in self.filters_data:
            for filter_key, trans_key in self.filters_data[category]:
                if USE_TRANSLATIONS:
                    display_name = Translations.get(trans_key, self.current_lang)
                else:
                    display_name = filter_key
                self.filter_combo.addItem(display_name, filter_key)

    def on_filter_changed(self):
        """تغییر فیلتر"""
        filter_key = self.filter_combo.currentData()
        if filter_key:
            params = {
                "blur_amount": self.blur_slider.value(),
                "clahe": self.clahe_spin.value(),
            }
            self.filter_changed.emit(filter_key, params)

    def on_params_changed(self):
        """تغییر پارامترها"""
        self.on_filter_changed()
