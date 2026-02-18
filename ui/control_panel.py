"""
پنل کنترل با پارامترهای داینامیک
Control Panel with Dynamic Parameters
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
    QCheckBox,
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
    custom_kernel_clicked = Signal()
    transformation_clicked = Signal()

    def __init__(self):
        super().__init__()

        if USE_TRANSLATIONS:
            self.settings = get_settings()
            self.current_lang = self.settings.get("language", "fa")
        else:
            self.current_lang = "fa"

        self.param_widgets = {}
        self.current_filter = None
        self.auto_apply = True

        self.setup_ui()
        if USE_TRANSLATIONS:
            self.set_show_hints(self.settings.get("show_hints", True))

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # NOTE: Control panel can have many params (e.g. Harris) and must not break
        # the layout when the window is resized. We put all groups inside a QScrollArea.
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setStyleSheet(
            """
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical { width: 10px; }
            """
        )

        # Widget inside scroll
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(config.Layout.SPACING_SMALL)
        scroll_layout.setContentsMargins(
            config.Layout.PADDING_SMALL,
            config.Layout.PADDING_SMALL,
            config.Layout.PADDING_SMALL,
            config.Layout.PADDING_SMALL,
        )

        # عنوان
        if USE_TRANSLATIONS:
            title_text = Translations.get("control_panel", self.current_lang)
        else:
            title_text = "Control Panel"

        title = QLabel(f"⚙️ {title_text}")
        title.setStyleSheet(
            f"""
            QLabel {{
                color: {config.Colors.PRIMARY};
                font-size: {config.Fonts.SIZE_HEADER}px;  # ✅ 11px
                font-weight: 600;
                padding: {config.Layout.PADDING_SMALL}px;
            }}
        """
        )
        main_layout.addWidget(title)

        # ✅ اول پارامترها رو بساز (قبل از فیلترها!)
        self.params_group = self.create_params_group()

        # ✅ بعد فیلترها
        filter_group = self.create_filter_group()
        scroll_layout.addWidget(filter_group)

        # ✅ بعد پارامترها
        scroll_layout.addWidget(self.params_group)

        # ✅ Apply + Toggle
        self.apply_group = self.create_apply_group()
        scroll_layout.addWidget(self.apply_group)

        # عملیات
        self.operations_group = self.create_operations_group()
        scroll_layout.addWidget(self.operations_group)

        # Zoom
        self.zoom_group = self.create_zoom_group()
        scroll_layout.addWidget(self.zoom_group)

        scroll_layout.addStretch(1)

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll, 1)

        # راهنما
        self.hint_label = QLabel(
            "💡 " + Translations.get("hint_default", self.current_lang)
        )
        self.hint_label.setStyleSheet(
            f"""
            QLabel {{
                color: {config.Colors.TEXT_MUTED};
                font-size: 10px;
                padding: 4px;
            }}
        """
        )
        main_layout.addWidget(self.hint_label)

        # Hint system (contextual)
        self._hint_registry = {}
        self._install_hints()

    def _install_hints(self):
        """Register contextual hints for key controls."""
        if not USE_TRANSLATIONS:
            return
        # Groups / controls
        try:
            self._register_hint(self.category_combo, "hint_filters")
            self._register_hint(self.filter_combo, "hint_filters")
        except Exception:
            pass
        # Parameters area (scroll)
        try:
            self._register_hint(self.params_container, "hint_params")
        except Exception:
            pass
        # Apply
        try:
            self._register_hint(self.apply_btn, "hint_apply")
            self._register_hint(self.auto_apply_cb, "hint_auto_apply")
        except Exception:
            pass
        # Operations
        try:
            self._register_hint(self.load_btn, "hint_load")
            self._register_hint(self.save_btn, "hint_save")
            self._register_hint(self.settings_btn, "hint_settings")
        except Exception:
            pass
        # Zoom
        try:
            self._register_hint(self.zoom_in_btn, "hint_zoom_in")
            self._register_hint(self.zoom_out_btn, "hint_zoom_out")
            self._register_hint(self.reset_zoom_btn, "hint_reset_zoom")
            self._register_hint(self.reset_all_btn, "hint_reset_all")
        except Exception:
            pass

    def _register_hint(self, widget, key: str):
        """Attach tooltip + connect hover/focus to bottom hint label."""
        if widget is None:
            return
        self._hint_registry[widget] = key
        widget.setToolTip(Translations.get(key, self.current_lang))
        widget.installEventFilter(self)

    def eventFilter(self, obj, event):
        if self.settings.get("show_hints", True) and hasattr(self, "hint_label"):
            try:
                from PySide6.QtCore import QEvent

                if event.type() in (
                    QEvent.Enter,
                    QEvent.FocusIn,
                    QEvent.MouseButtonPress,
                ):
                    if obj in self._hint_registry:
                        self.hint_label.setText("💡 " + obj.toolTip())
                elif event.type() in (QEvent.Leave, QEvent.FocusOut):
                    # revert to default hint
                    self.hint_label.setText(
                        "💡 " + Translations.get("hint_default", self.current_lang)
                    )
            except Exception:
                pass
        return super().eventFilter(obj, event)

    def create_apply_group(self):
        """گروه Apply و Auto-Apply"""
        group = QGroupBox("🎯 " + Translations.get("apply_group", self.current_lang))
        layout = QVBoxLayout()
        layout.setSpacing(6)

        # ✅ Toggle برای Auto-Apply
        auto_layout = QHBoxLayout()
        self.auto_apply_check = QCheckBox(
            Translations.get("auto_apply", self.current_lang)
        )
        self.auto_apply_check.setChecked(True)
        self.auto_apply_check.setToolTip(
            "When enabled, filter applies automatically.\n"
            "When disabled, you need to click Apply button."
        )

        # ✅ استفاده از toggled به جای stateChanged
        self.auto_apply_check.toggled.connect(self.on_auto_apply_toggled)

        auto_layout.addWidget(self.auto_apply_check)
        layout.addLayout(auto_layout)

        # ✅ دکمه Apply
        self.apply_btn = QPushButton(
            "✅ " + Translations.get("apply_filter_btn", self.current_lang)
        )
        self.apply_btn.setMinimumHeight(config.Layout.BUTTON_HEIGHT)
        self.apply_btn.setEnabled(False)
        self.apply_btn.clicked.connect(self.on_apply_clicked)
        layout.addWidget(self.apply_btn)

        group.setLayout(layout)
        return group

    def on_auto_apply_toggled(self, checked):
        """✅ تغییر حالت Auto-Apply - با toggled signal"""
        was_auto = self.auto_apply
        self.auto_apply = checked

        print(f"[Auto-Apply] Toggled: {was_auto} → {self.auto_apply}")

        # ✅ فعال/غیرفعال کردن دکمه Apply
        self.apply_btn.setEnabled(not self.auto_apply)

        # ✅ اگر auto-apply فعال شد و فیلتر داریم، فوراً اعمال کن
        if self.auto_apply and not was_auto and self.current_filter:
            print(f"[Auto-Apply] Just enabled! Applying filter: {self.current_filter}")
            params = self.get_current_params()
            self.filter_changed.emit(self.current_filter, params)

    def on_auto_apply_changed(self, state):
        was_auto = self.auto_apply
        self.auto_apply = state == Qt.Checked

        print(f"[Auto-Apply] Changed: {was_auto} → {self.auto_apply}")  # Debug

        self.apply_btn.setEnabled(not self.auto_apply)

        if self.auto_apply and self.current_filter:
            print(f"[Auto-Apply] Applying filter: {self.current_filter}")  # Debug
            params = self.get_current_params()
            self.filter_changed.emit(self.current_filter, params)

        if self.auto_apply:
            self.reconnect_param_signals()

    def reconnect_param_signals(self):
        """✅ اتصال مجدد signal های پارامترها"""
        for param_name, widget in self.param_widgets.items():
            if isinstance(widget, QSlider):
                # قطع و وصل مجدد
                try:
                    widget.valueChanged.disconnect()
                except:
                    pass
                widget.valueChanged.connect(self.on_params_changed)

            elif isinstance(widget, (QDoubleSpinBox, QSpinBox)):
                try:
                    widget.valueChanged.disconnect()
                except:
                    pass
                widget.valueChanged.connect(self.on_params_changed)

    def on_apply_clicked(self):
        """کلیک روی دکمه Apply"""
        if self.current_filter:
            params = self.get_current_params()
            self.filter_changed.emit(self.current_filter, params)

    def reset_to_defaults(self):
        """ریست کامل پنل فیلترها (دسته‌بندی/فیلتر/پارامترها) به حالت پیش‌فرض."""
        if not hasattr(self, "category_combo") or not hasattr(self, "filter_combo"):
            return

        # جلوگیری از auto-apply هنگام ریست
        self.category_combo.blockSignals(True)
        self.filter_combo.blockSignals(True)

        # Base همیشه اولین گزینه است
        self.category_combo.setCurrentIndex(0)

        # بازسازی لیست فیلترها و پارامترها
        self.on_category_changed(0)

        # اطمینان از انتخاب "original"
        idx = self.filter_combo.findData("original")
        if idx >= 0:
            self.filter_combo.setCurrentIndex(idx)

        self.filter_combo.blockSignals(False)
        self.category_combo.blockSignals(False)

    def create_filter_group(self):
        """گروه فیلتر"""
        group = QGroupBox("🎨 " + Translations.get("filters_group", self.current_lang))
        layout = QVBoxLayout()
        layout.setSpacing(6)

        # دستهبندی
        self.category_combo = QComboBox()
        self.category_combo.setMinimumHeight(config.Layout.CONTROL_HEIGHT)

        if USE_TRANSLATIONS:
            self.category_combo.addItem(
                "🎨 " + Translations.get("category_base", self.current_lang), "base"
            )
            self.category_combo.addItem(
                "✨ " + Translations.get("category_enhancement", self.current_lang),
                "edge",
            )
            self.category_combo.addItem(
                "📷 " + Translations.get("category_photogrammetry", self.current_lang),
                "photogrammetry",
            )
            self.category_combo.addItem("🎨 Color", "color")
            self.category_combo.addItem(
                "🎭 " + Translations.get("category_advanced", self.current_lang),
                "creative",
            )
            self.category_combo.addItem("🔲 Convolution", "convolution")
            self.category_combo.addItem(
                "📍 " + Translations.get("category_point_detection", self.current_lang),
                "point_detection",
            )
            self.category_combo.addItem("🔄 Transformation", "transformation")
        else:
            self.category_combo.addItem("🎨 Base", "base")
            self.category_combo.addItem("✨ Edge Detection", "edge")
            self.category_combo.addItem("📷 Photogrammetry", "photogrammetry")
            self.category_combo.addItem("🌈 Color", "color")
            self.category_combo.addItem("🎭 Creative", "creative")
            self.category_combo.addItem("🔲 Convolution", "convolution")
            self.category_combo.addItem("📍 Point Detection", "point_detection")
            self.category_combo.addItem("🔄 Transformation", "transformation")

        self.category_combo.currentIndexChanged.connect(self.on_category_changed)
        layout.addWidget(self.category_combo)

        # فیلتر
        self.filter_combo = QComboBox()
        self.filter_combo.setMinimumHeight(config.Layout.CONTROL_HEIGHT)
        self.filter_combo.currentIndexChanged.connect(self.on_filter_changed)
        layout.addWidget(self.filter_combo)

        group.setLayout(layout)

        # پر کردن فیلترها
        self.populate_filters()

        return group

    def create_params_group(self):
        """گروه پارامترها - داینامیک"""
        group = QGroupBox("⚙️ " + Translations.get("params_group", self.current_lang))

        # Layout اصلی که داینامیک میشه
        self.params_container = QWidget()
        self.params_layout = QVBoxLayout(self.params_container)
        self.params_layout.setSpacing(6)
        self.params_layout.setContentsMargins(0, 0, 0, 0)

        # پیغام پیشفرض
        self.no_params_label = QLabel(
            "ℹ️ " + Translations.get("no_params", self.current_lang)
        )
        self.no_params_label.setAlignment(Qt.AlignCenter)
        self.no_params_label.setStyleSheet(
            f"""
            QLabel {{
                color: {config.Colors.TEXT_MUTED};
                padding: 20px;
                font-size: {config.Fonts.SIZE_SMALL}px;
            }}
        """
        )
        self.params_layout.addWidget(self.no_params_label)

        group_layout = QVBoxLayout()
        group_layout.setContentsMargins(8, 8, 8, 8)
        group_layout.addWidget(self.params_container)
        group.setLayout(group_layout)

        return group

    def create_operations_group(self):
        """گروه عملیات"""
        group = QGroupBox(
            "🔧 " + Translations.get("operations_group", self.current_lang)
        )
        layout = QGridLayout()
        layout.setSpacing(6)

        self.load_btn = QPushButton(
            "📂 " + Translations.get("load_image", self.current_lang)
        )
        self.load_btn.setMinimumHeight(config.Layout.BUTTON_HEIGHT)
        self.load_btn.clicked.connect(self.load_clicked.emit)

        self.save_btn = QPushButton(
            "💾 " + Translations.get("save_image", self.current_lang)
        )
        self.save_btn.setMinimumHeight(config.Layout.BUTTON_HEIGHT)
        self.save_btn.clicked.connect(self.save_clicked.emit)

        self.settings_btn = QPushButton(
            "⚙️ " + Translations.get("settings", self.current_lang)
        )
        self.settings_btn.setMinimumHeight(config.Layout.BUTTON_HEIGHT)
        self.settings_btn.clicked.connect(self.settings_clicked.emit)

        layout.addWidget(self.load_btn, 0, 0)
        layout.addWidget(self.save_btn, 0, 1)
        layout.addWidget(self.settings_btn, 1, 0, 1, 2)

        group.setLayout(layout)
        return group

    def create_zoom_group(self):
        """گروه Zoom"""
        group = QGroupBox("🔍 " + Translations.get("zoom_group", self.current_lang))
        layout = QGridLayout()
        layout.setSpacing(6)

        self.zoom_in_btn = QPushButton("➕")
        self.zoom_in_btn.setMinimumHeight(config.Layout.BUTTON_HEIGHT)
        self.zoom_in_btn.clicked.connect(self.zoom_in_clicked.emit)

        self.zoom_out_btn = QPushButton("➖")
        self.zoom_out_btn.setMinimumHeight(config.Layout.BUTTON_HEIGHT)
        self.zoom_out_btn.clicked.connect(self.zoom_out_clicked.emit)

        self.zoom_reset_btn = QPushButton("🔄 Reset")
        self.zoom_reset_btn.setMinimumHeight(config.Layout.BUTTON_HEIGHT)
        self.zoom_reset_btn.clicked.connect(self.zoom_reset_clicked.emit)

        self.reset_btn = QPushButton(
            "↺ " + Translations.get("reset_all", self.current_lang)
        )
        self.reset_btn.setProperty("variant", "danger")
        self.reset_btn.setMinimumHeight(config.Layout.BUTTON_HEIGHT)
        self.reset_btn.clicked.connect(self.reset_clicked.emit)

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
                ("original", "Original"),
                ("grayscale", "Grayscale"),
                ("blur", "Blur"),
                ("sharpen", "Sharpen"),
                ("bilateral", "Bilateral Filter"),
                ("median", "Median Filter"),
                ("histogram_equalization", "Histogram Equalization"),
                ("clahe", "CLAHE"),
            ],
            "edge": [
                # Project #4 expects the manual (step-by-step) Canny as the main option.
                ("edge_canny_project4", "Canny"),
                ("edge_canny", "Canny (OpenCV - آماده)"),
                ("edge_sobel", "Sobel"),
                ("edge_laplacian", "Laplacian"),
                ("edge_scharr", "Scharr"),
            ],
            "photogrammetry": [
                ("contrast_stretch", "Contrast Stretch"),
                ("gamma_correction", "Gamma Correction"),
                ("threshold_binary", "Binary Threshold"),
                ("threshold_otsu", "Otsu Threshold"),
                ("adaptive_threshold", "Adaptive Threshold"),
                ("morphology_erode", "Morphology Erode"),
                ("morphology_dilate", "Morphology Dilate"),
                ("morphology_open", "Morphology Open"),
                ("morphology_close", "Morphology Close"),
            ],
            "color": [
                ("hsv", "HSV"),
                ("lab", "LAB"),
                ("hue_shift", "Hue Shift"),
                ("saturation_adjust", "Saturation Adjust"),
                ("brightness_adjust", "Brightness Adjust"),
                ("temperature_adjust", "Temperature Adjust"),
                ("invert_colors", "Invert Colors"),
            ],
            "creative": [
                ("clay", "Clay"),
                ("negative", "Negative"),
                ("sepia", "Sepia"),
                ("emboss", "Emboss"),
                ("cartoon", "Cartoon"),
                ("pencil_sketch", "Pencil Sketch"),
                ("oil_painting", "Oil Painting"),
                ("watercolor", "Watercolor"),
            ],
            "convolution": [
                ("conv_sobel_x", "Sobel X"),
                ("conv_sobel_y", "Sobel Y"),
                ("conv_sobel_combined", "Sobel Combined"),
                ("conv_prewitt_x", "Prewitt X"),
                ("conv_prewitt_y", "Prewitt Y"),
                ("conv_prewitt_combined", "Prewitt Combined"),
                ("conv_laplacian", "Laplacian"),
                ("conv_laplacian_diag", "Laplacian Diagonal"),
                ("conv_sharpen_basic", "Sharpen Basic"),
                ("conv_sharpen_strong", "Sharpen Strong"),
                ("conv_unsharp", "Unsharp Mask"),
                ("conv_box_blur", "Box Blur"),
                ("conv_gaussian", "Gaussian Blur"),
                ("conv_emboss", "Emboss"),
                ("conv_emboss_subtle", "Emboss Subtle"),
                ("conv_edge_enhance", "Edge Enhance"),
                ("conv_outline", "Outline"),
                ("conv_custom", "🎨 Custom Kernel"),
            ],
            "point_detection": [
                ("moravec_corner", "Moravec"),
                ("haralick_corner", "Haralick"),
                ("harris_corner", "Harris"),
            ],
        }

        self.on_category_changed(0)

    def on_category_changed(self, index):
        category = self.category_combo.currentData()

        print(f"[Category Changed] Selected: {category}")  # Debug

        if category == "transformation":
            print("[Category] Opening Transformation dialog directly")
            self.transformation_clicked.emit()
            self.category_combo.blockSignals(True)
            self.filter_combo.blockSignals(True)
            self.category_combo.setCurrentIndex(0)
            self.filter_combo.blockSignals(False)
            self.category_combo.blockSignals(False)
            category = "base"  # ← اجباری به base تغییر بده

        self.filter_combo.blockSignals(True)
        self.filter_combo.clear()

        if category in self.filters_data:
            for filter_key, display_name in self.filters_data[category]:
                self.filter_combo.addItem(display_name, filter_key)

        self.filter_combo.blockSignals(False)

        if self.filter_combo.count() > 0:
            filter_key = self.filter_combo.currentData()
            if filter_key:
                self.current_filter = filter_key
                self.clear_params()
                self.create_filter_params(filter_key)

    def on_filter_changed(self):
        """تغییر فیلتر - بروزرسانی پارامترها"""
        filter_key = self.filter_combo.currentData()

        if not filter_key:
            return

        print(f"[Filter Changed] Selected: {filter_key}")

        if filter_key == "conv_custom":
            print("[Filter Changed] Opening Custom Kernel dialog")
            self.custom_kernel_clicked.emit()
            return

        self.current_filter = filter_key

        self.clear_params()

        self.create_filter_params(filter_key)

        if self.auto_apply:
            params = self.get_current_params()
            self.filter_changed.emit(filter_key, params)

    def clear_params(self):
        """پاک کردن همه پارامترها"""
        if not hasattr(self, "params_container"):
            return

        # ✅ حذف container قدیمی
        old_container = self.params_container
        old_container.setParent(None)
        old_container.deleteLater()

        # ✅ ساخت container جدید
        self.params_container = QWidget()
        self.params_layout = QVBoxLayout(self.params_container)
        self.params_layout.setSpacing(6)
        self.params_layout.setContentsMargins(0, 0, 0, 0)

        # ✅ اضافه کردن به group
        self.params_group.layout().addWidget(self.params_container)

        # پاک کردن دیکشنری
        self.param_widgets.clear()

    def create_filter_params(self, filter_key):
        if not hasattr(self, "params_layout"):
            return

        params_config = self.get_params_config(filter_key)

        if not params_config:
            # اگر پارامتری نداشت
            self.no_params_label = QLabel(
                "ℹ️ " + Translations.get("no_params", self.current_lang)
            )
            self.no_params_label.setAlignment(Qt.AlignCenter)
            self.no_params_label.setStyleSheet(
                f"""
                QLabel {{
                    color: {config.Colors.TEXT_MUTED};
                    padding: 20px;
                    font-size: {config.Fonts.SIZE_SMALL}px;
                }}
            """
            )
            self.params_layout.addWidget(self.no_params_label)
            return

        # ساخت پارامترها
        for param_name, param_config in params_config.items():
            self.create_param_widget(param_name, param_config)

    def get_params_config(self, filter_key):
        """تعریف پارامترها برای هر فیلتر"""
        configs = {
            # Base Filters
            "blur": {
                "ksize": {
                    "type": "slider",
                    "min": 1,
                    "max": 99,
                    "default": 15,
                    "step": 2,
                    "label": "Kernel Size",
                },
            },
            "clahe": {
                "clipLimit": {
                    "type": "double",
                    "min": 0.1,
                    "max": 10.0,
                    "default": 2.0,
                    "step": 0.1,
                    "label": "Clip Limit",
                },
                "tileGridSize": {
                    "type": "slider",
                    "min": 2,
                    "max": 16,
                    "default": 8,
                    "step": 1,
                    "label": "Tile Size",
                },
            },
            "bilateral": {
                "d": {
                    "type": "slider",
                    "min": 5,
                    "max": 25,
                    "default": 9,
                    "step": 2,
                    "label": "Diameter",
                },
                "sigmaColor": {
                    "type": "slider",
                    "min": 10,
                    "max": 200,
                    "default": 75,
                    "step": 5,
                    "label": "Sigma Color",
                },
                "sigmaSpace": {
                    "type": "slider",
                    "min": 10,
                    "max": 200,
                    "default": 75,
                    "step": 5,
                    "label": "Sigma Space",
                },
            },
            "median": {
                "ksize": {
                    "type": "slider",
                    "min": 3,
                    "max": 31,
                    "default": 5,
                    "step": 2,
                    "label": "Kernel Size",
                },
            },
            # Edge Filters
            "edge_canny": {
                "threshold1": {
                    "type": "slider",
                    "min": 0,
                    "max": 300,
                    "default": 100,
                    "step": 10,
                    "label": "Threshold 1",
                },
                "threshold2": {
                    "type": "slider",
                    "min": 0,
                    "max": 300,
                    "default": 200,
                    "step": 10,
                    "label": "Threshold 2",
                },
            },
            "edge_canny_project4": {
                "gaussian_ksize": {
                    "type": "slider",
                    "min": 3,
                    "max": 15,
                    "default": 5,
                    "step": 2,
                    "label": "Gaussian Kernel Size",
                },
                "low_threshold": {
                    "type": "slider",
                    "min": 0,
                    "max": 255,
                    "default": 50,
                    "step": 5,
                    "label": "Low Threshold",
                },
                "high_threshold": {
                    "type": "slider",
                    "min": 0,
                    "max": 255,
                    "default": 150,
                    "step": 5,
                    "label": "High Threshold",
                },
            },
            # Color Filters
            "hue_shift": {
                "shift": {
                    "type": "slider",
                    "min": 0,
                    "max": 180,
                    "default": 30,
                    "step": 5,
                    "label": "Hue Shift",
                },
            },
            "saturation_adjust": {
                "factor": {
                    "type": "double",
                    "min": 0.0,
                    "max": 3.0,
                    "default": 1.5,
                    "step": 0.1,
                    "label": "Saturation",
                },
            },
            "brightness_adjust": {
                "value": {
                    "type": "slider",
                    "min": -100,
                    "max": 100,
                    "default": 50,
                    "step": 5,
                    "label": "Brightness",
                },
            },
            "temperature_adjust": {
                "temperature": {
                    "type": "slider",
                    "min": -100,
                    "max": 100,
                    "default": 0,
                    "step": 5,
                    "label": "Temperature",
                },
            },
            # Photogrammetry
            "contrast_stretch": {
                "min_percentile": {
                    "type": "slider",
                    "min": 0,
                    "max": 10,
                    "default": 2,
                    "step": 1,
                    "label": "Min %",
                },
                "max_percentile": {
                    "type": "slider",
                    "min": 90,
                    "max": 100,
                    "default": 98,
                    "step": 1,
                    "label": "Max %",
                },
            },
            "gamma_correction": {
                "gamma": {
                    "type": "double",
                    "min": 0.1,
                    "max": 5.0,
                    "default": 1.0,
                    "step": 0.1,
                    "label": "Gamma",
                },
            },
            "threshold_binary": {
                "threshold": {
                    "type": "slider",
                    "min": 0,
                    "max": 255,
                    "default": 127,
                    "step": 1,
                    "label": "Threshold",
                },
            },
            "adaptive_threshold": {
                "blockSize": {
                    "type": "slider",
                    "min": 3,
                    "max": 99,
                    "default": 11,
                    "step": 2,
                    "label": "Block Size",
                },
                "C": {
                    "type": "slider",
                    "min": -20,
                    "max": 20,
                    "default": 2,
                    "step": 1,
                    "label": "Constant C",
                },
            },
            "morphology_erode": {
                "kernel_size": {
                    "type": "slider",
                    "min": 3,
                    "max": 21,
                    "default": 5,
                    "step": 2,
                    "label": "Kernel Size",
                },
            },
            "morphology_dilate": {
                "kernel_size": {
                    "type": "slider",
                    "min": 3,
                    "max": 21,
                    "default": 5,
                    "step": 2,
                    "label": "Kernel Size",
                },
            },
            "morphology_open": {
                "kernel_size": {
                    "type": "slider",
                    "min": 3,
                    "max": 21,
                    "default": 5,
                    "step": 2,
                    "label": "Kernel Size",
                },
            },
            "morphology_close": {
                "kernel_size": {
                    "type": "slider",
                    "min": 3,
                    "max": 21,
                    "default": 5,
                    "step": 2,
                    "label": "Kernel Size",
                },
            },
            # Creative
            "oil_painting": {
                "size": {
                    "type": "slider",
                    "min": 1,
                    "max": 15,
                    "default": 7,
                    "step": 2,
                    "label": "Size",
                },
                "dynRatio": {
                    "type": "slider",
                    "min": 1,
                    "max": 10,
                    "default": 1,
                    "step": 1,
                    "label": "Dynamic Ratio",
                },
            },
            # Point Detection (Project #3)
            "moravec_corner": {
                "threshold": {
                    "type": "double",
                    "min": 0.0,
                    "max": 50000.0,
                    "default": 2500.0,
                    "step": 50.0,
                    "label": "Threshold",
                },
                "nms_window": {
                    "type": "slider",
                    "min": 3,
                    "max": 31,
                    "default": 7,
                    "step": 2,
                    "label": "Local Max Window",
                },
                "max_points": {
                    "type": "slider",
                    "min": 0,
                    "max": 1000,
                    "default": 300,
                    "step": 50,
                    "label": "Max Points (0=all)",
                },
                "circle_radius": {
                    "type": "slider",
                    "min": 1,
                    "max": 10,
                    "default": 3,
                    "step": 1,
                    "label": "Circle Radius",
                },
                "circle_thickness": {
                    "type": "slider",
                    "min": 1,
                    "max": 5,
                    "default": 1,
                    "step": 1,
                    "label": "Circle Thickness",
                },
            },
            "haralick_corner": {
                # Using percentile makes the threshold robust across different images.
                # Threshold is applied on w=det(Hessian) (higher is more corner-like).
                "thresh_w": {
                    "type": "double",
                    "min": 0.0,
                    "max": 1000000000.0,
                    "default": 0.0,
                    "step": 1000.0,
                    "label": "Threshold w (0=auto)",
                    "decimals": 2,
                },
                "thresh_q": {
                    "type": "double",
                    "min": 0.0,
                    "max": 1.0,
                    "default": 0.5,
                    "step": 0.05,
                    "label": "Threshold q",
                    "decimals": 2,
                },
                "nms_window": {
                    "type": "slider",
                    "min": 3,
                    "max": 31,
                    "default": 7,
                    "step": 2,
                    "label": "Local Max Window",
                },
                "max_points": {
                    "type": "slider",
                    "min": 0,
                    "max": 1000,
                    "default": 300,
                    "step": 50,
                    "label": "Max Points (0=all)",
                },
                "circle_radius": {
                    "type": "slider",
                    "min": 1,
                    "max": 10,
                    "default": 3,
                    "step": 1,
                    "label": "Circle Radius",
                },
                "circle_thickness": {
                    "type": "slider",
                    "min": 1,
                    "max": 5,
                    "default": 1,
                    "step": 1,
                    "label": "Circle Thickness",
                },
            },
            "harris_corner": {
                # Percentile threshold is far more usable than a raw huge-number threshold.
                # It selects top responses from R=det(H)-trace(H)^2.
                "threshold_r": {
                    "type": "double",
                    "min": 0.0,
                    "max": 1000000000.0,
                    "default": 0.0,
                    "step": 1000.0,
                    "label": "Threshold R (0=auto)",
                    "decimals": 2,
                },
                "gaussian_ksize": {
                    "type": "slider",
                    "min": 3,
                    "max": 31,
                    "default": 5,
                    "step": 2,
                    "label": "Gaussian Kernel",
                },
                "gaussian_sigma": {
                    "type": "double",
                    "min": 0.1,
                    "max": 10.0,
                    "default": 1.0,
                    "step": 0.1,
                    "label": "Gaussian Sigma",
                    "decimals": 2,
                },
                "nms_window": {
                    "type": "slider",
                    "min": 3,
                    "max": 31,
                    "default": 7,
                    "step": 2,
                    "label": "Local Max Window",
                },
                "max_points": {
                    "type": "slider",
                    "min": 0,
                    "max": 1000,
                    "default": 300,
                    "step": 50,
                    "label": "Max Points (0=all)",
                },
                "circle_radius": {
                    "type": "slider",
                    "min": 1,
                    "max": 10,
                    "default": 3,
                    "step": 1,
                    "label": "Circle Radius",
                },
                "circle_thickness": {
                    "type": "slider",
                    "min": 1,
                    "max": 5,
                    "default": 1,
                    "step": 1,
                    "label": "Circle Thickness",
                },
            },
        }

        return configs.get(filter_key, {})

    def create_param_widget(self, param_name, config):
        """ساخت ویجت پارامتر"""
        if not hasattr(self, "params_layout"):
            return

        # Use a row widget so layouts can properly calculate size hints.
        # This prevents the left panel from "breaking" when params count grows.
        row = QWidget()
        grid = QGridLayout(row)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(0)
        grid.setColumnStretch(1, 1)  # control expands

        # Label (wraps if needed)
        label = QLabel(config["label"] + ":")
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        # Keep label flexible but readable; it can wrap on narrow widths.
        from PySide6.QtWidgets import QSizePolicy

        label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        grid.addWidget(label, 0, 0)

        if config["type"] == "slider":
            # Slider + Value Label
            slider = QSlider(Qt.Horizontal)
            slider.setMinimum(config["min"])
            slider.setMaximum(config["max"])
            slider.setValue(config["default"])
            slider.setSingleStep(config.get("step", 1))
            slider.setMinimumHeight(20)

            slider.setSizePolicy(
                slider.sizePolicy().horizontalPolicy(),
                slider.sizePolicy().verticalPolicy(),
            )

            value_label = QLabel(str(config["default"]))
            value_label.setMinimumWidth(44)
            value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

            # ✅ Lambda برای update label
            slider.valueChanged.connect(lambda v: value_label.setText(str(v)))

            # ✅ اتصال به on_params_changed
            slider.valueChanged.connect(self.on_params_changed)

            grid.addWidget(slider, 0, 1)
            grid.addWidget(value_label, 0, 2)

            self.param_widgets[param_name] = slider

        elif config["type"] == "double":
            # Double SpinBox
            spinbox = QDoubleSpinBox()
            spinbox.setRange(config["min"], config["max"])
            spinbox.setValue(config["default"])
            spinbox.setSingleStep(config.get("step", 0.1))
            spinbox.setMinimumHeight(28)
            spinbox.setDecimals(config.get("decimals", 3))

            # ✅ اتصال به on_params_changed
            spinbox.valueChanged.connect(self.on_params_changed)

            grid.addWidget(spinbox, 0, 1, 1, 2)

            self.param_widgets[param_name] = spinbox

        self.params_layout.addWidget(row)

    def get_current_params(self):
        """دریافت پارامترهای فعلی"""
        params = {}

        for param_name, widget in self.param_widgets.items():
            if isinstance(widget, QSlider):
                params[param_name] = widget.value()
            elif isinstance(widget, QDoubleSpinBox):
                params[param_name] = widget.value()
            elif isinstance(widget, QSpinBox):
                params[param_name] = widget.value()

        return params

    def on_params_changed(self):
        """✅ تغییر پارامترها با لاگ"""
        print(f"[Params] Changed. Auto-apply: {self.auto_apply}")  # Debug

        if self.auto_apply and self.current_filter:
            params = self.get_current_params()
            print(
                f"[Params] Emitting filter_changed for: {self.current_filter}"
            )  # Debug
            self.filter_changed.emit(self.current_filter, params)
        else:
            print(
                f"[Params] Not applying (auto_apply={self.auto_apply}, filter={self.current_filter})"
            )

    def set_show_hints(self, enabled: bool):
        """نمایش/مخفی کردن راهنمای پایین پنل"""
        if hasattr(self, "hint_label") and self.hint_label is not None:
            self.hint_label.setVisible(bool(enabled))

    def set_language(self, lang: str):
        """اعمال زبان در لحظه برای متن‌های پنل کنترل"""
        if not USE_TRANSLATIONS:
            return
        self.current_lang = lang or "fa"
        self.setLayoutDirection(
            Qt.RightToLeft if self.current_lang == "fa" else Qt.LeftToRight
        )

        # Titles
        try:
            self.filters_group.setTitle(
                "🎨 " + Translations.get("filters_group", self.current_lang)
            )
        except Exception:
            pass
        try:
            self.params_group.setTitle(
                "🧪 " + Translations.get("params_group", self.current_lang)
            )
        except Exception:
            pass
        try:
            self.apply_group.setTitle(
                "🎯 " + Translations.get("apply_group", self.current_lang)
            )
        except Exception:
            pass
        try:
            self.operations_group.setTitle(
                "🛠️ " + Translations.get("operations_group", self.current_lang)
            )
        except Exception:
            pass
        try:
            self.zoom_group.setTitle(
                "🔍 " + Translations.get("zoom_group", self.current_lang)
            )
        except Exception:
            pass

        # Buttons (if exist)
        if hasattr(self, "load_btn"):
            self.load_btn.setText(
                "📂 " + Translations.get("load_image", self.current_lang)
            )
        if hasattr(self, "save_btn"):
            self.save_btn.setText(
                "💾 " + Translations.get("save_image", self.current_lang)
            )
        if hasattr(self, "reset_btn"):
            self.reset_btn.setText("🔄 " + Translations.get("reset", self.current_lang))
        if hasattr(self, "settings_btn"):
            self.settings_btn.setText(
                "⚙️ " + Translations.get("settings_title", self.current_lang)
            )

        if hasattr(self, "auto_apply_check"):
            self.auto_apply_check.setText(
                Translations.get("auto_apply", self.current_lang)
            )
        if hasattr(self, "apply_btn"):
            self.apply_btn.setText(
                "✅ " + Translations.get("apply_filter_btn", self.current_lang)
            )

        # Hint
        if hasattr(self, "hint_label"):
            self.hint_label.setText(
                "💡 " + Translations.get("hint_zoom_wheel", self.current_lang)
            )
