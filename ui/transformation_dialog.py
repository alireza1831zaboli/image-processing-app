"""
دیالوگ Transformation بهبود یافته
- ورودی دستی (SpinBox) + Slider
- فعال/غیرفعال شدن Interpolation
- بهینه‌سازی سرعت
"""

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QGroupBox,
    QRadioButton,
    QSlider,
    QDoubleSpinBox,
    QSpinBox,
    QGridLayout,
    QFrame,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import numpy as np
import config

# Fix PRIMARY_HOVER
if not hasattr(config.Colors, "PRIMARY_HOVER"):
    config.Colors.PRIMARY_HOVER = "#0078D4"


class TransformationDialog(QDialog):
    """دیالوگ تنظیمات Transformation"""

    transformation_ready = Signal(str, dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔄 Geometric Transformation")
        self.setModal(True)
        self.resize(550, 650)

        # مقادیر پیش‌فرض
        self.rotation = 45.0
        self.scale = 2.0
        self.brightness = 256
        self.method = "direct"
        self.interpolation = "nn"

        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        """ساخت رابط کاربری"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # عنوان
        title = QLabel("⚙️ Geometric Transformation Settings")
        title_font = QFont()
        title_font.setPointSize(13)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # توضیح
        desc = QLabel(
            "Configure rotation, scale, and brightness parameters.\n"
            "Choose between Direct Mapping or Inverse Mapping methods."
        )
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet(f"color: {config.Colors.TEXT_MUTED}; padding: 5px;")
        main_layout.addWidget(desc)

        # جداکننده
        line1 = QFrame()
        line1.setFrameShape(QFrame.HLine)
        line1.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line1)

        # پارامترهای اصلی
        params_group = self.create_parameters_group()
        main_layout.addWidget(params_group)

        # جداکننده
        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line2)

        # انتخاب روش
        method_group = self.create_method_group()
        main_layout.addWidget(method_group)

        # دکمه‌ها
        buttons_layout = self.create_buttons()
        main_layout.addLayout(buttons_layout)

    def create_parameters_group(self):
        """ساخت گروه پارامترها"""
        group = QGroupBox("📐 Transformation Parameters")
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # ✅ R: Rotation با SpinBox
        rotation_container = self.create_param_with_spinbox(
            label="R: Rotation (degrees)",
            min_val=0,
            max_val=360,
            default=45,
            is_double=False,
            param_name="rotation",
            icon="🔄",
        )
        layout.addLayout(rotation_container)

        # ✅ S: Scale با SpinBox
        scale_container = self.create_param_with_spinbox(
            label="S: Scale",
            min_val=0.1,
            max_val=5.0,
            default=2.0,
            is_double=True,
            param_name="scale",
            icon="🔍",
        )
        layout.addLayout(scale_container)

        # ✅ B: Brightness با SpinBox
        brightness_container = self.create_param_with_spinbox(
            label="B: Brightness",
            min_val=0,
            max_val=512,
            default=256,
            is_double=False,
            param_name="brightness",
            icon="💡",
        )
        layout.addLayout(brightness_container)

        group.setLayout(layout)
        return group

    def create_param_with_spinbox(
        self, label, min_val, max_val, default, is_double, param_name, icon=""
    ):
        """✅ ساخت Slider + SpinBox برای ورودی دقیق"""
        container = QVBoxLayout()
        container.setSpacing(8)

        # Header
        header = QHBoxLayout()
        label_widget = QLabel(f"{icon} {label}")
        label_widget.setStyleSheet("font-weight: 600; font-size: 11pt;")
        header.addWidget(label_widget)
        header.addStretch()

        # ✅ SpinBox برای ورودی دستی
        if is_double:
            spinbox = QDoubleSpinBox()
            spinbox.setRange(min_val, max_val)
            spinbox.setValue(default)
            spinbox.setSingleStep(0.1)
            spinbox.setDecimals(1)
        else:
            spinbox = QSpinBox()
            spinbox.setRange(int(min_val), int(max_val))
            spinbox.setValue(int(default))
            spinbox.setSingleStep(1)

        spinbox.setMinimumWidth(80)
        spinbox.setStyleSheet(
            f"""
            QSpinBox, QDoubleSpinBox {{
                background-color: {config.Colors.PRIMARY};
                color: white;
                padding: 4px 8px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11pt;
            }}
            """
        )
        header.addWidget(spinbox)
        container.addLayout(header)

        # ✅ Slider
        slider = QSlider(Qt.Horizontal)
        if is_double:
            slider.setMinimum(int(min_val * 10))
            slider.setMaximum(int(max_val * 10))
            slider.setValue(int(default * 10))
        else:
            slider.setMinimum(int(min_val))
            slider.setMaximum(int(max_val))
            slider.setValue(int(default))

        slider.setTickPosition(QSlider.TicksBelow)
        slider.setTickInterval(
            (max_val - min_val) // 10 if (max_val - min_val) > 10 else 1
        )
        slider.setMinimumHeight(30)

        # ✅ اتصال دو طرفه: Slider <-> SpinBox
        if is_double:
            slider.valueChanged.connect(lambda v: spinbox.setValue(v / 10.0))
            spinbox.valueChanged.connect(lambda v: slider.setValue(int(v * 10)))
            spinbox.valueChanged.connect(lambda v: setattr(self, param_name, v))
        else:
            slider.valueChanged.connect(lambda v: spinbox.setValue(v))
            spinbox.valueChanged.connect(lambda v: slider.setValue(v))
            spinbox.valueChanged.connect(lambda v: setattr(self, param_name, v))

        container.addWidget(slider)

        # ذخیره reference
        setattr(self, f"{param_name}_slider", slider)
        setattr(self, f"{param_name}_spinbox", spinbox)

        return container

    def create_method_group(self):
        """ساخت گروه انتخاب روش"""
        group = QGroupBox("🔧 Mapping Method")
        layout = QVBoxLayout()
        layout.setSpacing(12)

        # راهنما
        info = QLabel(
            "Direct Map: Forward mapping (may have holes)\n"
            "Inverse Map: Backward mapping (no holes, needs interpolation)"
        )
        info.setStyleSheet(
            f"""
            color: {config.Colors.TEXT_MUTED};
            background-color: {config.Colors.WIDGET};
            padding: 8px;
            border-radius: 4px;
            font-size: 9pt;
        """
        )
        layout.addWidget(info)

        self.directradio = QRadioButton("✓ Direct Map")
        self.directradio.setStyleSheet("font-weight: 600; font-size: 10pt;")

        self.inverseradio = QRadioButton("⊙ Inverse Map")
        self.inverseradio.setStyleSheet("font-weight: 600; font-size: 10pt;")

        layout.addWidget(self.directradio)
        layout.addWidget(self.inverseradio)
        
        self.interpolationgroup = self.create_interpolation_group()
        layout.addWidget(self.interpolationgroup)

        self.directradio.toggled.connect(self.on_method_changed)
        self.inverseradio.toggled.connect(self.on_method_changed)

        self.directradio.setChecked(True)

        group.setLayout(layout)
        return group

    def create_interpolation_group(self):
        """ساخت گروه انتخاب Interpolation"""
        group = QGroupBox("🎯 Interpolation Method (for Inverse Map)")
        layout = QVBoxLayout()
        layout.setSpacing(8)

        # NN
        self.nn_radio = QRadioButton("NN - Nearest Neighbor")
        self.nn_radio.setChecked(True)
        self.nn_radio.setToolTip("Fastest, lowest quality")
        layout.addWidget(self.nn_radio)

        # BL
        self.bilinear_radio = QRadioButton("BL - Bilinear")
        self.bilinear_radio.setToolTip("Medium speed, good quality")
        layout.addWidget(self.bilinear_radio)

        # BC
        self.bicubic_radio = QRadioButton("BC - Bicubic")
        self.bicubic_radio.setToolTip("Slowest, highest quality")
        layout.addWidget(self.bicubic_radio)

        group.setLayout(layout)
        return group

    def create_buttons(self):
        """ساخت دکمه‌ها"""
        layout = QHBoxLayout()
        layout.setSpacing(10)

        # Reset
        reset_btn = QPushButton("🔄 Reset")
        reset_btn.setMinimumHeight(40)
        reset_btn.clicked.connect(self.reset_values)
        layout.addWidget(reset_btn)

        layout.addStretch()

        # Cancel
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.setMinimumHeight(40)
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn)

        # Apply
        primary_hover = getattr(config.Colors, "PRIMARY_HOVER", "#0078D4")
        apply_btn = QPushButton("✅ Apply Transformation")
        apply_btn.setMinimumHeight(40)
        apply_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {config.Colors.PRIMARY};
                color: white;
                font-weight: bold;
                font-size: 11pt;
                border-radius: 6px;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background-color: {primary_hover};
            }}
            """
        )
        apply_btn.clicked.connect(self.apply_transformation)
        layout.addWidget(apply_btn)

        return layout

    def on_method_changed(self):
        """Handle method change - enable/disable interpolation"""
        if self.inverseradio.isChecked():
            self.method = "inverse"
            self.interpolationgroup.setEnabled(True)
            self.interpolationgroup.setStyleSheet("")
        else:
            self.method = "direct"
            self.interpolationgroup.setEnabled(False)
            self.interpolationgroup.setStyleSheet(
                f"""
                QGroupBox {{
                    color: {config.Colors.TEXT_MUTED};
                }}
                QRadioButton {{
                    color: {config.Colors.TEXT_MUTED};
                }}
            """
            )

        print(
            f"[Method Changed] {self.method}, Interpolation enabled: {self.interpolationgroup.isEnabled()}"
        )

    def reset_values(self):
        """بازگشت به مقادیر پیش‌فرض"""
        self.rotation_spinbox.setValue(45)
        self.scale_spinbox.setValue(2.0)
        self.brightness_spinbox.setValue(256)

        self.direct_radio.setChecked(True)
        self.nn_radio.setChecked(True)

    def apply_transformation(self):
        """اعمال تبدیل"""
        # تعیین روش
        if self.method == "direct":
            method = "transform_direct"
        else:
            if self.nn_radio.isChecked():
                method = "transform_inverse_nn"
            elif self.bilinear_radio.isChecked():
                method = "transform_inverse_bilinear"
            else:
                method = "transform_inverse_bicubic"

        # پارامترها
        params = {
            "rotation": float(self.rotation),
            "scale": float(self.scale),
            "brightness": int(self.brightness) - 256,
        }

        print(
            f"[Dialog] Transformation: {method}, R={params['rotation']}, "
            f"S={params['scale']}, B={params['brightness']}"
        )

        self.transformation_ready.emit(method, params)
        self.accept()

    def apply_styles(self):
        """اعمال استایل‌ها"""
        primary_hover = getattr(config.Colors, "PRIMARY_HOVER", "#0078D4")

        self.setStyleSheet(
            f"""
            QDialog {{
                background-color: {config.Colors.BACKGROUND};
            }}
            QGroupBox {{
                background-color: {config.Colors.WIDGET};
                border: 2px solid {config.Colors.BORDER};
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 15px;
                font-weight: bold;
                font-size: 11pt;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: {config.Colors.PRIMARY};
            }}
            QRadioButton {{
                spacing: 8px;
                color: {config.Colors.TEXT};
                padding: 5px;
            }}
            QRadioButton::indicator {{
                width: 18px;
                height: 18px;
            }}
            QRadioButton::indicator:checked {{
                background-color: {config.Colors.PRIMARY};
                border: 2px solid {config.Colors.PRIMARY};
                border-radius: 9px;
            }}
            QRadioButton::indicator:unchecked {{
                background-color: {config.Colors.BACKGROUND};
                border: 2px solid {config.Colors.BORDER};
                border-radius: 9px;
            }}
            QSlider::groove:horizontal {{
                border: 1px solid {config.Colors.BORDER};
                height: 8px;
                background: {config.Colors.BACKGROUND};
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                background: {config.Colors.PRIMARY};
                border: 2px solid {primary_hover};
                width: 20px;
                margin: -6px 0;
                border-radius: 10px;
            }}
            QSlider::handle:horizontal:hover {{
                background: {primary_hover};
            }}
            QPushButton {{
                background-color: {config.Colors.WIDGET};
                color: {config.Colors.TEXT};
                border: 2px solid {config.Colors.BORDER};
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 10pt;
            }}
            QPushButton:hover {{
                background-color: {config.Colors.PANEL};
                border-color: {config.Colors.PRIMARY};
            }}
            """
        )
