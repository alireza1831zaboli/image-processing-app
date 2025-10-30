"""
پنل کنترل فیلترها
Control Panel
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QComboBox,
    QSlider,
    QGroupBox,
    QGridLayout,
    QSpinBox,
    QDoubleSpinBox,
    QTabWidget,
)
from PySide6.QtCore import Qt, Signal


class ControlPanel(QWidget):
    """پنل کنترل فیلترها"""

    filter_changed = Signal(str, dict)  # سیگنال تغییر فیلتر
    load_clicked = Signal()
    save_clicked = Signal()
    reset_clicked = Signal()

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        """ساخت UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # دکمه بارگذاری
        load_btn = QPushButton("📁 بارگذاری تصویر")
        load_btn.setMinimumHeight(50)
        load_btn.clicked.connect(self.load_clicked.emit)
        layout.addWidget(load_btn)

        # تب‌های فیلترها
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_basic_tab(), "پایه")
        self.tabs.addTab(self.create_edge_tab(), "لبه‌یابی")
        self.tabs.addTab(self.create_photo_tab(), "فوتوگرامتری")
        self.tabs.addTab(self.create_creative_tab(), "خلاقانه")
        self.tabs.addTab(self.create_color_tab(), "رنگ")
        layout.addWidget(self.tabs)

        # دکمه‌های عملیاتی
        action_group = self.create_action_buttons()
        layout.addWidget(action_group)

        layout.addStretch()

    def create_basic_tab(self):
        """تب فیلترهای پایه"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.basic_combo = QComboBox()
        filters = [
            ("اصلی", "original"),
            ("خاکستری", "grayscale"),
            ("محو کردن", "blur"),
            ("تیز کردن", "sharpen"),
            ("فیلتر دو سویه", "bilateral"),
            ("فیلتر میانه", "median"),
            ("هیستوگرام", "histogram_equalization"),
            ("CLAHE", "clahe"),
        ]
        for name, value in filters:
            self.basic_combo.addItem(name, value)

        self.basic_combo.currentIndexChanged.connect(self.on_filter_changed)
        layout.addWidget(QLabel("انتخاب فیلتر:"))
        layout.addWidget(self.basic_combo)

        # پارامترها
        param_group = QGroupBox("تنظیمات")
        param_layout = QGridLayout(param_group)

        param_layout.addWidget(QLabel("اندازه Blur:"), 0, 0)
        self.blur_slider = QSlider(Qt.Horizontal)
        self.blur_slider.setRange(1, 31)
        self.blur_slider.setValue(15)
        self.blur_slider.setSingleStep(2)
        self.blur_slider.valueChanged.connect(self.on_filter_changed)
        param_layout.addWidget(self.blur_slider, 0, 1)
        self.blur_label = QLabel("15")
        self.blur_slider.valueChanged.connect(lambda v: self.blur_label.setText(str(v)))
        param_layout.addWidget(self.blur_label, 0, 2)

        param_layout.addWidget(QLabel("CLAHE:"), 1, 0)
        self.clahe_spin = QDoubleSpinBox()
        self.clahe_spin.setRange(0.1, 10.0)
        self.clahe_spin.setValue(2.0)
        self.clahe_spin.valueChanged.connect(self.on_filter_changed)
        param_layout.addWidget(self.clahe_spin, 1, 1, 1, 2)

        layout.addWidget(param_group)
        layout.addStretch()
        return widget

    def create_edge_tab(self):
        """تب لبه‌یابی"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.edge_combo = QComboBox()
        filters = [
            ("Canny", "edge_canny"),
            ("Sobel", "edge_sobel"),
            ("Laplacian", "edge_laplacian"),
            ("Scharr", "edge_scharr"),
        ]
        for name, value in filters:
            self.edge_combo.addItem(name, value)

        self.edge_combo.currentIndexChanged.connect(self.on_filter_changed)
        layout.addWidget(QLabel("انتخاب الگوریتم:"))
        layout.addWidget(self.edge_combo)

        # پارامترهای Canny
        param_group = QGroupBox("تنظیمات Canny")
        param_layout = QGridLayout(param_group)

        param_layout.addWidget(QLabel("آستانه پایین:"), 0, 0)
        self.canny_low_slider = QSlider(Qt.Horizontal)
        self.canny_low_slider.setRange(0, 255)
        self.canny_low_slider.setValue(100)
        self.canny_low_slider.valueChanged.connect(self.on_filter_changed)
        param_layout.addWidget(self.canny_low_slider, 0, 1)
        self.canny_low_label = QLabel("100")
        self.canny_low_slider.valueChanged.connect(
            lambda v: self.canny_low_label.setText(str(v))
        )
        param_layout.addWidget(self.canny_low_label, 0, 2)

        param_layout.addWidget(QLabel("آستانه بالا:"), 1, 0)
        self.canny_high_slider = QSlider(Qt.Horizontal)
        self.canny_high_slider.setRange(0, 255)
        self.canny_high_slider.setValue(200)
        self.canny_high_slider.valueChanged.connect(self.on_filter_changed)
        param_layout.addWidget(self.canny_high_slider, 1, 1)
        self.canny_high_label = QLabel("200")
        self.canny_high_slider.valueChanged.connect(
            lambda v: self.canny_high_label.setText(str(v))
        )
        param_layout.addWidget(self.canny_high_label, 1, 2)

        layout.addWidget(param_group)
        layout.addStretch()
        return widget

    def create_photo_tab(self):
        """تب فوتوگرامتری"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.photo_combo = QComboBox()
        filters = [
            ("کشش کنتراست", "contrast_stretch"),
            ("تصحیح گاما", "gamma_correction"),
            ("آستانه‌گذاری", "threshold_binary"),
            ("Otsu", "threshold_otsu"),
            ("آستانه تطبیقی", "adaptive_threshold"),
            ("فرسایش", "morphology_erode"),
            ("انبساط", "morphology_dilate"),
        ]
        for name, value in filters:
            self.photo_combo.addItem(name, value)

        self.photo_combo.currentIndexChanged.connect(self.on_filter_changed)
        layout.addWidget(QLabel("انتخاب فیلتر:"))
        layout.addWidget(self.photo_combo)

        # پارامترها
        param_group = QGroupBox("تنظیمات")
        param_layout = QGridLayout(param_group)

        param_layout.addWidget(QLabel("گاما:"), 0, 0)
        self.gamma_spin = QDoubleSpinBox()
        self.gamma_spin.setRange(0.1, 5.0)
        self.gamma_spin.setValue(1.0)
        self.gamma_spin.setSingleStep(0.1)
        self.gamma_spin.valueChanged.connect(self.on_filter_changed)
        param_layout.addWidget(self.gamma_spin, 0, 1)

        param_layout.addWidget(QLabel("آستانه:"), 1, 0)
        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setRange(0, 255)
        self.threshold_slider.setValue(127)
        self.threshold_slider.valueChanged.connect(self.on_filter_changed)
        param_layout.addWidget(self.threshold_slider, 1, 1)
        self.threshold_label = QLabel("127")
        self.threshold_slider.valueChanged.connect(
            lambda v: self.threshold_label.setText(str(v))
        )
        param_layout.addWidget(self.threshold_label, 1, 2)

        layout.addWidget(param_group)
        layout.addStretch()
        return widget

    def create_creative_tab(self):
        """تب خلاقانه"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.creative_combo = QComboBox()
        filters = [
            ("گلی (Clay)", "clay"),
            ("منفی (Negative)", "negative"),
            ("سپیا", "sepia"),
            ("برجسته", "emboss"),
            ("کارتونی", "cartoon"),
            ("طراحی مداد", "pencil_sketch"),
            ("آبرنگ", "watercolor"),
        ]
        for name, value in filters:
            self.creative_combo.addItem(name, value)

        self.creative_combo.currentIndexChanged.connect(self.on_filter_changed)
        layout.addWidget(QLabel("انتخاب افکت:"))
        layout.addWidget(self.creative_combo)

        layout.addStretch()
        return widget

    def create_color_tab(self):
        """تب رنگ"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.color_combo = QComboBox()
        filters = [
            ("HSV", "hsv"),
            ("LAB", "lab"),
            ("تغییر رنگ", "hue_shift"),
            ("اشباع", "saturation_adjust"),
            ("روشنایی", "brightness_adjust"),
            ("دمای رنگ", "temperature_adjust"),
        ]
        for name, value in filters:
            self.color_combo.addItem(name, value)

        self.color_combo.currentIndexChanged.connect(self.on_filter_changed)
        layout.addWidget(QLabel("انتخاب عملیات:"))
        layout.addWidget(self.color_combo)

        # پارامترها
        param_group = QGroupBox("تنظیمات")
        param_layout = QGridLayout(param_group)

        param_layout.addWidget(QLabel("تغییر رنگ:"), 0, 0)
        self.hue_slider = QSlider(Qt.Horizontal)
        self.hue_slider.setRange(-180, 180)
        self.hue_slider.setValue(0)
        self.hue_slider.valueChanged.connect(self.on_filter_changed)
        param_layout.addWidget(self.hue_slider, 0, 1)
        self.hue_label = QLabel("0")
        self.hue_slider.valueChanged.connect(lambda v: self.hue_label.setText(str(v)))
        param_layout.addWidget(self.hue_label, 0, 2)

        param_layout.addWidget(QLabel("اشباع:"), 1, 0)
        self.saturation_spin = QDoubleSpinBox()
        self.saturation_spin.setRange(0.0, 3.0)
        self.saturation_spin.setValue(1.0)
        self.saturation_spin.setSingleStep(0.1)
        self.saturation_spin.valueChanged.connect(self.on_filter_changed)
        param_layout.addWidget(self.saturation_spin, 1, 1, 1, 2)

        param_layout.addWidget(QLabel("روشنایی:"), 2, 0)
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(-100, 100)
        self.brightness_slider.setValue(0)
        self.brightness_slider.valueChanged.connect(self.on_filter_changed)
        param_layout.addWidget(self.brightness_slider, 2, 1)
        self.brightness_label = QLabel("0")
        self.brightness_slider.valueChanged.connect(
            lambda v: self.brightness_label.setText(str(v))
        )
        param_layout.addWidget(self.brightness_label, 2, 2)

        layout.addWidget(param_group)
        layout.addStretch()
        return widget

    def create_action_buttons(self):
        """دکمه‌های عملیاتی"""
        group = QGroupBox("عملیات")
        layout = QVBoxLayout(group)

        reset_btn = QPushButton("🔄 بازگشت به اصل")
        reset_btn.clicked.connect(self.reset_clicked.emit)
        layout.addWidget(reset_btn)

        save_btn = QPushButton("💾 ذخیره تصویر")
        save_btn.clicked.connect(self.save_clicked.emit)
        layout.addWidget(save_btn)

        apply_btn = QPushButton("✓ اعمال فیلتر")
        apply_btn.setStyleSheet("background-color: #4CAF50;")
        apply_btn.clicked.connect(self.on_filter_changed)
        layout.addWidget(apply_btn)

        # دکمه‌های Zoom
        zoom_layout = QHBoxLayout()
        zoom_in_btn = QPushButton("🔍+")
        zoom_out_btn = QPushButton("🔍-")
        zoom_reset_btn = QPushButton("⊙")

        zoom_layout.addWidget(zoom_in_btn)
        zoom_layout.addWidget(zoom_out_btn)
        zoom_layout.addWidget(zoom_reset_btn)
        layout.addLayout(zoom_layout)

        # اتصال سیگنال‌های zoom به mainwindow
        zoom_in_btn.clicked.connect(lambda: self.parent().zoom_in())
        zoom_out_btn.clicked.connect(lambda: self.parent().zoom_out())
        zoom_reset_btn.clicked.connect(lambda: self.parent().reset_zoom())

        return group

    def on_filter_changed(self):
        """تغییر فیلتر"""
        filter_name = self.get_active_filter()
        params = self.get_current_params()
        self.filter_changed.emit(filter_name, params)

    def get_active_filter(self):
        """دریافت فیلتر فعال"""
        current_tab = self.tabs.currentIndex()
        if current_tab == 0:
            return self.basic_combo.currentData()
        elif current_tab == 1:
            return self.edge_combo.currentData()
        elif current_tab == 2:
            return self.photo_combo.currentData()
        elif current_tab == 3:
            return self.creative_combo.currentData()
        elif current_tab == 4:
            return self.color_combo.currentData()
        return "original"

    def get_current_params(self):
        """دریافت پارامترهای فعلی"""
        return {
            "ksize": self.blur_slider.value(),
            "clipLimit": self.clahe_spin.value(),
            "threshold1": self.canny_low_slider.value(),
            "threshold2": self.canny_high_slider.value(),
            "gamma": self.gamma_spin.value(),
            "threshold": self.threshold_slider.value(),
            "shift": self.hue_slider.value(),
            "factor": self.saturation_spin.value(),
            "value": self.brightness_slider.value(),
        }
