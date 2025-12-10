"""
پنل کنترل فشرده و بهینه شده
Compact and Optimized Control Panel
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
    QGridLayout,
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


# در ابتدای فایل، سیگنال جدید اضافه کن:
class ControlPanel(QWidget):
    filter_changed = Signal(str, dict)
    load_clicked = Signal()
    save_clicked = Signal()
    reset_clicked = Signal()
    settings_clicked = Signal()
    zoom_in_clicked = Signal()
    zoom_out_clicked = Signal()
    zoom_reset_clicked = Signal()
    custom_kernel_clicked = Signal()

    def __init__(self):
        super().__init__()
        if USE_TRANSLATIONS:
            self.settings = get_settings()
            self.current_lang = self.settings.get("language", "fa")
        else:
            self.current_lang = "fa"
        self.setup_ui()

    def setup_ui(self):
        """ساخت UI فشرده"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(8, 8, 8, 8)

        # عنوان کوچک
        if USE_TRANSLATIONS:
            title_text = Translations.get("control_panel", self.current_lang)
        else:
            title_text = "Control Panel"

        title = QLabel(f"⚙️ {title_text}")
        title.setStyleSheet(
            f"""
            QLabel {{
                color: {config.Colors.PRIMARY};
                font-size: {config.Fonts.SIZE_HEADER}px;
                font-weight: 600;
                padding: 6px;
            }}
        """
        )
        main_layout.addWidget(title)

        # گروه فیلترها - فشرده
        filter_group = self.create_filter_group()
        main_layout.addWidget(filter_group)

        # پارامترها - فشرده
        params_group = self.create_params_group()
        main_layout.addWidget(params_group)

        # عملیات - Grid Layout برای فشردگی
        operations_group = self.create_operations_group()
        main_layout.addWidget(operations_group)

        # Zoom - فشرده
        zoom_group = self.create_zoom_group()
        main_layout.addWidget(zoom_group)

        main_layout.addStretch()

        # راهنما
        hint = QLabel("💡 Mouse Wheel: Zoom")
        hint.setStyleSheet(
            f"""
            QLabel {{
                color: {config.Colors.TEXT_MUTED};
                font-size: {config.Fonts.SIZE_SMALL}px;
                padding: 4px;
            }}
        """
        )
        main_layout.addWidget(hint)

    def create_filter_group(self):
        """گروه فیلتر - فشرده"""
        group = QGroupBox("🎨 Filters")
        layout = QVBoxLayout()
        layout.setSpacing(6)

        # دسته‌بندی
        self.category_combo = QComboBox()
        self.category_combo.setMinimumHeight(config.Layout.CONTROL_HEIGHT)
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
            self.category_combo.addItem(
                "🔲 " + Translations.get("category_Convolution", self.current_lang),
                "convolution",
            )

        else:
            self.category_combo.addItem("🎨 Base", "base")
            self.category_combo.addItem("✨ Enhancement", "enhancement")
            self.category_combo.addItem("📷 Photogrammetry", "photogrammetry")
            self.category_combo.addItem("🎭 Creative", "advanced")
            self.category_combo.addItem("🔲 Convolution", "convolution")

        self.category_combo.currentIndexChanged.connect(self.on_category_changed)
        layout.addWidget(self.category_combo)

        self.filter_combo = QComboBox()
        self.filter_combo.setMinimumHeight(config.Layout.CONTROL_HEIGHT)
        self.filter_combo.blockSignals(True)
        self.filter_combo.currentIndexChanged.connect(self.on_filter_changed)
        layout.addWidget(self.filter_combo)

        group.setLayout(layout)
        self.populate_filters()
        self.filter_combo.blockSignals(False)
        return group

    def create_params_group(self):
        """گروه پارامترها - فشرده"""
        group = QGroupBox("⚙️ Parameters")
        layout = QVBoxLayout()
        layout.setSpacing(6)

        # Blur - inline
        blur_container = QHBoxLayout()
        blur_container.setSpacing(6)
        blur_label = QLabel("Blur:")
        blur_label.setFixedWidth(45)
        self.blur_slider = QSlider(Qt.Horizontal)
        self.blur_slider.setRange(1, 30)
        self.blur_slider.setValue(15)
        self.blur_slider.setMinimumHeight(24)
        self.blur_slider.valueChanged.connect(self.on_params_changed)
        self.blur_value_label = QLabel("15")
        self.blur_value_label.setFixedWidth(25)
        self.blur_value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.blur_slider.valueChanged.connect(
            lambda v: self.blur_value_label.setText(str(v))
        )
        blur_container.addWidget(blur_label)
        blur_container.addWidget(self.blur_slider)
        blur_container.addWidget(self.blur_value_label)
        layout.addLayout(blur_container)

        # CLAHE - inline
        clahe_container = QHBoxLayout()
        clahe_container.setSpacing(6)
        clahe_label = QLabel("CLAHE:")
        clahe_label.setFixedWidth(45)
        self.clahe_spin = QDoubleSpinBox()
        self.clahe_spin.setRange(1.0, 5.0)
        self.clahe_spin.setSingleStep(0.1)
        self.clahe_spin.setValue(2.0)
        self.clahe_spin.setMinimumHeight(config.Layout.CONTROL_HEIGHT)
        self.clahe_spin.valueChanged.connect(self.on_params_changed)
        clahe_container.addWidget(clahe_label)
        clahe_container.addWidget(self.clahe_spin)
        layout.addLayout(clahe_container)

        group.setLayout(layout)
        return group

    def create_operations_group(self):
        """گروه عملیات - Grid برای فشردگی"""
        group = QGroupBox("🔧 Operations")
        layout = QGridLayout()
        layout.setSpacing(6)

        # دکمه‌های کوچک‌تر
        self.load_btn = QPushButton("📁 Load")
        self.load_btn.setMinimumHeight(config.Layout.BUTTON_HEIGHT)
        self.load_btn.clicked.connect(self.load_clicked.emit)

        self.save_btn = QPushButton("💾 Save")
        self.save_btn.setMinimumHeight(config.Layout.BUTTON_HEIGHT)
        self.save_btn.clicked.connect(self.save_clicked.emit)

        self.settings_btn = QPushButton("⚙️ Settings")
        self.settings_btn.setMinimumHeight(config.Layout.BUTTON_HEIGHT)
        self.settings_btn.clicked.connect(self.settings_clicked.emit)

        # Grid 2x2
        layout.addWidget(self.load_btn, 0, 0)
        layout.addWidget(self.save_btn, 0, 1)
        layout.addWidget(self.settings_btn, 1, 0, 1, 2)  # full width

        group.setLayout(layout)
        return group

    def create_zoom_group(self):
        """گروه Zoom - فشرده Grid"""
        group = QGroupBox("🔍 Zoom")
        layout = QGridLayout()
        layout.setSpacing(6)

        # دکمه‌های کوچک
        self.zoom_in_btn = QPushButton("➕")
        self.zoom_in_btn.setMinimumHeight(32)
        self.zoom_in_btn.setMaximumWidth(60)
        self.zoom_in_btn.clicked.connect(self.zoom_in_clicked.emit)

        self.zoom_out_btn = QPushButton("➖")
        self.zoom_out_btn.setMinimumHeight(32)
        self.zoom_out_btn.setMaximumWidth(60)
        self.zoom_out_btn.clicked.connect(self.zoom_out_clicked.emit)

        self.zoom_reset_btn = QPushButton("🔄 Reset")
        self.zoom_reset_btn.setMinimumHeight(32)
        self.zoom_reset_btn.clicked.connect(self.zoom_reset_clicked.emit)

        self.reset_btn = QPushButton("↺ Reset All")
        self.reset_btn.setMinimumHeight(32)
        self.reset_btn.clicked.connect(self.reset_clicked.emit)

        # Grid 2x2
        layout.addWidget(self.zoom_in_btn, 0, 0)
        layout.addWidget(self.zoom_out_btn, 0, 1)
        layout.addWidget(self.zoom_reset_btn, 1, 0, 1, 2)
        layout.addWidget(self.reset_btn, 2, 0, 1, 2)

        group.setLayout(layout)
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
                ("gamma_correction", "filter_gamma"),
                ("threshold_binary", "filter_threshold"),
                ("threshold_otsu", "filter_otsu"),
                ("morphology_erode", "filter_morphology"),
            ],
            "convolution": [  # جدید!
                ("conv_sobel_combined", "Sobel (Combined)"),
                ("conv_prewitt_combined", "Prewitt (Combined)"),
                ("conv_laplacian", "Laplacian"),
                ("conv_laplacian_diag", "Laplacian (Diagonal)"),
                ("conv_sharpen_basic", "Sharpen Basic"),
                ("conv_sharpen_strong", "Sharpen Strong"),
                ("conv_emboss", "Emboss"),
                ("conv_outline", "Outline"),
                ("conv_edge_enhance", "Edge Enhance"),
                ("conv_custom", "🎨 Custom Kernel"),
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
                ("saturation_adjust", "filter_saturation"),
                ("brightness_adjust", "filter_brightness"),
                ("temperature_adjust", "filter_temperature"),
            ],
        }
        self.on_category_changed(0)

    def on_category_changed(self, index):
        """تغییر دستهبندی"""
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
            if filter_key == "conv_custom":
                self.custom_kernel_clicked.emit()
                return

            params = {
                "ksize": self.blur_slider.value(),
                "clipLimit": self.clahe_spin.value(),
            }
            self.filter_changed.emit(filter_key, params)

    def on_params_changed(self):
        """تغییر پارامترها"""
        self.on_filter_changed()
