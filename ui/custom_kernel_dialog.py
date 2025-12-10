"""
دیالوگ Custom Kernel - نسخه نهایی
Custom Kernel Dialog - Only Matrix Scrollable
"""

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QCheckBox,
    QGroupBox,
    QMessageBox,
    QFrame,
    QScrollArea,
    QWidget,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDoubleValidator
import numpy as np
import config


class CustomKernelDialog(QDialog):
    """دیالوگ طراحی Custom Kernel با ماشین‌حساب"""

    kernel_ready = Signal(np.ndarray, bool, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🎨 Custom Convolution Kernel Designer")
        self.setModal(True)
        self.setMinimumSize(650, 700)

        self.kernel_size = 3
        self.kernel_inputs = []
        self.calculator_display = ""
        self.selected_cell = None

        self.setup_ui()
        self.apply_styles()
        self.create_kernel_grid()

    def setup_ui(self):
        """ساخت UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        # عنوان
        title = QLabel("🎨 Custom Kernel Designer")
        title.setStyleSheet(
            f"""
            QLabel {{
                font-size: 20px;
                font-weight: 600;
                color: {config.Colors.PRIMARY};
                padding: 8px;
            }}
        """
        )
        layout.addWidget(title)

        # Layout افقی برای تنظیمات و پیش‌نمایش
        top_layout = QHBoxLayout()

        # ========== ستون چپ: تنظیمات ==========
        settings_col = QVBoxLayout()

        # انتخاب سایز
        size_group = QGroupBox("📐 Kernel Size")
        size_layout = QHBoxLayout()

        size_label = QLabel("Size:")
        self.size_combo = QComboBox()
        self.size_combo.addItems(["3×3", "5×5", "7×7", "9×9", "11×11"])
        self.size_combo.currentIndexChanged.connect(self.on_size_changed)

        size_layout.addWidget(size_label)
        size_layout.addWidget(self.size_combo)

        size_group.setLayout(size_layout)
        settings_col.addWidget(size_group)

        # انتخاب Padding
        padding_group = QGroupBox("🔲 Padding Type")
        padding_layout = QVBoxLayout()

        self.padding_combo = QComboBox()
        self.padding_combo.addItem("🔄 Replicate (Repeat Edges)", "replicate")
        self.padding_combo.addItem("🪞 Reflect (Mirror)", "reflect")
        self.padding_combo.addItem("⭕ Zero Padding", "zero")
        self.padding_combo.addItem("🔁 Wrap (Circular)", "wrap")
        self.padding_combo.addItem("❌ No Padding (Crop)", "none")

        padding_info = QLabel("💡 Replicate: Recommended for most cases")
        padding_info.setWordWrap(True)
        padding_info.setStyleSheet(
            f"color: {config.Colors.TEXT_SECONDARY}; font-size: 10px;"
        )

        padding_layout.addWidget(self.padding_combo)
        padding_layout.addWidget(padding_info)

        padding_group.setLayout(padding_layout)
        settings_col.addWidget(padding_group)

        # Presets
        presets_group = QGroupBox("🎯 Quick Presets")
        presets_layout = QGridLayout()
        presets_layout.setSpacing(4)

        presets = [
            ("Identity", "identity"),
            ("Sharpen", "sharpen"),
            ("Edge", "edge"),
            ("Blur", "blur"),
            ("Emboss", "emboss"),
            ("Laplacian", "laplacian"),
        ]

        row, col = 0, 0
        for name, preset in presets:
            btn = QPushButton(name)
            btn.setMaximumHeight(30)
            btn.clicked.connect(lambda checked, p=preset: self.load_preset(p))
            presets_layout.addWidget(btn, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1

        presets_group.setLayout(presets_layout)
        settings_col.addWidget(presets_group)

        settings_col.addStretch()

        top_layout.addLayout(settings_col, stretch=1)

        # ========== ستون راست: ماشین‌حساب ==========
        calc_group = QGroupBox("🧮 Calculator")
        calc_layout = QVBoxLayout()
        calc_layout.setSpacing(6)

        # نمایشگر
        self.calc_display = QLineEdit("0")
        self.calc_display.setReadOnly(False)
        self.calc_display.setAlignment(Qt.AlignRight)
        self.calc_display.setMinimumHeight(40)
        self.calc_display.returnPressed.connect(self.calculate_from_keyboard)
        self.calc_display.textChanged.connect(self.on_calc_text_changed)
        self.calc_display.setStyleSheet(
            f"""
            QLineEdit {{
                font-size: 18px;
                font-weight: 600;
                background-color: {config.Colors.BACKGROUND};
                border: 2px solid {config.Colors.PRIMARY};
                border-radius: 6px;
                padding: 8px;
            }}
        """
        )
        calc_layout.addWidget(self.calc_display)

        # دکمه‌های ماشین‌حساب
        calc_buttons_layout = QGridLayout()
        calc_buttons_layout.setSpacing(4)

        buttons = [
            ["7", "8", "9", "/"],
            ["4", "5", "6", "*"],
            ["1", "2", "3", "-"],
            ["0", ".", "=", "+"],
            ["C", "(", ")", "←"],
        ]

        for i, row in enumerate(buttons):
            for j, btn_text in enumerate(row):
                btn = QPushButton(btn_text)
                btn.setMinimumHeight(35)
                btn.setMaximumWidth(50)

                if btn_text == "=":
                    btn.setStyleSheet(f"background-color: {config.Colors.SUCCESS};")
                elif btn_text == "C":
                    btn.setStyleSheet(f"background-color: {config.Colors.ERROR};")
                elif btn_text in ["+", "-", "*", "/"]:
                    btn.setStyleSheet(
                        f"background-color: {config.Colors.PRIMARY_DARK};"
                    )

                btn.clicked.connect(
                    lambda checked, t=btn_text: self.calculator_click(t)
                )
                calc_buttons_layout.addWidget(btn, i, j)

        calc_layout.addLayout(calc_buttons_layout)

        # دکمه Apply Result
        apply_calc_btn = QPushButton("📋 Apply to Selected Cell")
        apply_calc_btn.clicked.connect(self.apply_calc_to_cell)
        calc_layout.addWidget(apply_calc_btn)

        calc_group.setLayout(calc_layout)
        top_layout.addWidget(calc_group, stretch=1)

        layout.addLayout(top_layout)

        # جداکننده
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        # ========== Kernel Matrix با ScrollArea ==========
        self.kernel_group = QGroupBox("🔢 Kernel Matrix")
        kernel_main_layout = QVBoxLayout()

        # ✅ ScrollArea فقط برای kernel matrix
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setMinimumHeight(200)
        scroll.setMaximumHeight(280)

        # Container widget برای grid
        kernel_container = QWidget()
        self.kernel_grid_layout = QGridLayout(kernel_container)
        self.kernel_grid_layout.setSpacing(6)
        self.kernel_grid_layout.setContentsMargins(10, 10, 10, 10)
        self.kernel_grid_layout.setAlignment(Qt.AlignCenter)

        scroll.setWidget(kernel_container)
        kernel_main_layout.addWidget(scroll)

        self.kernel_group.setLayout(kernel_main_layout)
        layout.addWidget(self.kernel_group)

        # ========== Options ==========
        options_layout = QHBoxLayout()

        self.normalize_check = QCheckBox("Normalize Output")
        self.normalize_check.setChecked(False)
        self.normalize_check.setToolTip("Normalize result to 0-255 range")

        self.auto_sum_check = QCheckBox("Auto-normalize Kernel (Σ=1)")
        self.auto_sum_check.setChecked(False)
        self.auto_sum_check.setToolTip(
            "Divide all values by sum (useful for blur kernels)"
        )

        self.show_sum_btn = QPushButton("Σ Show Sum")
        self.show_sum_btn.setMaximumWidth(100)
        self.show_sum_btn.clicked.connect(self.show_kernel_sum)

        options_layout.addWidget(self.normalize_check)
        options_layout.addWidget(self.auto_sum_check)
        options_layout.addWidget(self.show_sum_btn)
        options_layout.addStretch()

        layout.addLayout(options_layout)

        # ========== Buttons ==========
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        clear_btn = QPushButton("🗑️ Clear All")
        clear_btn.clicked.connect(self.clear_kernel)
        buttons_layout.addWidget(clear_btn)

        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)

        apply_btn = QPushButton("✅ Apply Kernel")
        apply_btn.setDefault(True)
        apply_btn.clicked.connect(self.apply_kernel)
        buttons_layout.addWidget(apply_btn)

        layout.addLayout(buttons_layout)

    def create_kernel_grid(self):
        """ساخت Grid برای ورودی kernel"""
        # پاک کردن grid قبلی
        for i in reversed(range(self.kernel_grid_layout.count())):
            widget = self.kernel_grid_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        self.kernel_inputs = []

        # ✅ سایز سل‌ها بر اساس kernel size
        if self.kernel_size <= 5:
            cell_width = 65
            cell_height = 40
        elif self.kernel_size <= 7:
            cell_width = 55
            cell_height = 36
        else:  # 9 یا 11
            cell_width = 50
            cell_height = 34

        # ساخت input های جدید
        for i in range(self.kernel_size):
            row_inputs = []
            for j in range(self.kernel_size):
                input_field = QLineEdit("0")
                input_field.setAlignment(Qt.AlignCenter)
                input_field.setFixedWidth(cell_width)
                input_field.setFixedHeight(cell_height)

                # Validator برای اعداد اعشاری
                validator = QDoubleValidator(-1000.0, 1000.0, 6)
                input_field.setValidator(validator)

                # رنگ مرکز
                if i == self.kernel_size // 2 and j == self.kernel_size // 2:
                    input_field.setStyleSheet(
                        f"""
                        QLineEdit {{
                            background-color: {config.Colors.PRIMARY};
                            color: white;
                            font-weight: 600;
                            font-size: 13px;
                        }}
                    """
                    )
                else:
                    input_field.setStyleSheet(
                        f"""
                        QLineEdit {{
                            font-size: 13px;
                            font-weight: 500;
                        }}
                    """
                    )

                # وقتی focus میشه، ذخیره کن
                input_field.focusInEvent = (
                    lambda event, cell=input_field: self.on_cell_focused(cell, event)
                )

                self.kernel_grid_layout.addWidget(input_field, i, j)
                row_inputs.append(input_field)

            self.kernel_inputs.append(row_inputs)

        # مقدار مرکزی رو 1 کن
        center = self.kernel_size // 2
        self.kernel_inputs[center][center].setText("1")

    def on_cell_focused(self, cell, event):
        """وقتی یک سل focus میشه"""
        self.selected_cell = cell
        QLineEdit.focusInEvent(cell, event)

    def on_size_changed(self, index):
        """تغییر سایز kernel"""
        sizes = [3, 5, 7, 9, 11]
        self.kernel_size = sizes[index]
        self.create_kernel_grid()

    def on_calc_text_changed(self, text):
        """وقتی متن calculator تغییر می‌کنه"""
        self.calculator_display = text

    def calculate_from_keyboard(self):
        """محاسبه با Enter از کیبورد"""
        self.calculator_click("=")

    def calculator_click(self, button_text):
        """کلیک روی دکمه‌های ماشین‌حساب"""
        if button_text == "=":
            try:
                result = eval(self.calculator_display)
                self.calc_display.setText(str(result))
                self.calculator_display = str(result)
            except:
                self.calc_display.setText("Error")
                self.calculator_display = ""
        elif button_text == "C":
            self.calc_display.setText("0")
            self.calculator_display = ""
        elif button_text == "←":
            current = self.calc_display.text()
            self.calc_display.setText(current[:-1] or "0")
        else:
            current = self.calc_display.text()
            if current == "0" and button_text not in [".", "+", "-", "*", "/"]:
                self.calc_display.setText(button_text)
            else:
                self.calc_display.setText(current + button_text)

    def apply_calc_to_cell(self):
        """اعمال نتیجه ماشین‌حساب به سل انتخاب شده"""
        if self.selected_cell is None:
            QMessageBox.warning(
                self, "No Cell Selected", "Please click on a kernel cell first!"
            )
            return

        is_kernel_cell = False
        for row in self.kernel_inputs:
            if self.selected_cell in row:
                is_kernel_cell = True
                break

        if not is_kernel_cell:
            QMessageBox.warning(
                self, "Invalid Cell", "Please select a cell from the kernel matrix!"
            )
            return

        result = self.calc_display.text()
        if result and result != "Error":
            try:
                float(result)
                self.selected_cell.setText(result)
            except ValueError:
                QMessageBox.warning(
                    self, "Invalid Value", "Please enter a valid number!"
                )
        else:
            QMessageBox.warning(self, "No Value", "Please calculate a value first!")

    def load_preset(self, preset: str):
        """بارگذاری preset آماده"""
        presets = {
            "identity": [[0, 0, 0], [0, 1, 0], [0, 0, 0]],
            "sharpen": [[0, -1, 0], [-1, 5, -1], [0, -1, 0]],
            "edge": [[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]],
            "blur": [
                [1 / 9, 1 / 9, 1 / 9],
                [1 / 9, 1 / 9, 1 / 9],
                [1 / 9, 1 / 9, 1 / 9],
            ],
            "emboss": [[-2, -1, 0], [-1, 1, 1], [0, 1, 2]],
            "laplacian": [[0, 1, 0], [1, -4, 1], [0, 1, 0]],
        }

        if preset in presets and self.kernel_size == 3:
            values = presets[preset]
            for i in range(3):
                for j in range(3):
                    self.kernel_inputs[i][j].setText(str(values[i][j]))
        elif self.kernel_size != 3:
            QMessageBox.warning(
                self,
                "Size Mismatch",
                "Presets are only available for 3×3 kernels.\nPlease select 3×3 size first.",
            )

    def clear_kernel(self):
        """پاک کردن همه مقادیر"""
        for i in range(self.kernel_size):
            for j in range(self.kernel_size):
                self.kernel_inputs[i][j].setText("0")

    def show_kernel_sum(self):
        """نمایش مجموع kernel"""
        kernel = self.get_kernel()
        kernel_sum = np.sum(kernel)
        QMessageBox.information(
            self,
            "Kernel Sum",
            f"Sum of all kernel values: {kernel_sum:.4f}\n\n"
            f"For blur kernels, sum should be 1.\n"
            f"For edge detection, sum should be 0.",
        )

    def get_kernel(self) -> np.ndarray:
        """دریافت kernel از ورودی‌ها"""
        kernel = np.zeros((self.kernel_size, self.kernel_size), dtype=np.float32)

        for i in range(self.kernel_size):
            for j in range(self.kernel_size):
                try:
                    value = float(self.kernel_inputs[i][j].text() or "0")
                    kernel[i, j] = value
                except ValueError:
                    kernel[i, j] = 0.0

        if self.auto_sum_check.isChecked():
            kernel_sum = np.sum(kernel)
            if abs(kernel_sum) > 1e-6:
                kernel = kernel / kernel_sum

        return kernel

    def apply_kernel(self):
        """اعمال kernel"""
        kernel = self.get_kernel()
        normalize = self.normalize_check.isChecked()
        padding = self.padding_combo.currentData()

        kernel_str = "\n".join([" ".join([f"{v:7.3f}" for v in row]) for row in kernel])

        msg = QMessageBox(self)
        msg.setWindowTitle("Confirm Kernel")
        msg.setText("Apply this custom kernel?")
        msg.setDetailedText(
            f"Kernel ({self.kernel_size}×{self.kernel_size}):\n{kernel_str}\n\n"
            f"Normalize: {normalize}\n"
            f"Padding: {padding}\n"
            f"Sum: {np.sum(kernel):.4f}"
        )
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.Yes)

        if msg.exec() == QMessageBox.Yes:
            self.kernel_ready.emit(kernel, normalize, padding)
            self.accept()

    def apply_styles(self):
        """استایل دیالوگ"""
        self.setStyleSheet(
            f"""
            QDialog {{
                background-color: {config.Colors.BACKGROUND};
                color: {config.Colors.TEXT};
            }}
            
            QGroupBox {{
                border: 1px solid {config.Colors.BORDER};
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 16px;
                font-weight: 500;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px;
            }}
            
            QLineEdit {{
                background-color: {config.Colors.WIDGET};
                border: 1px solid {config.Colors.BORDER};
                border-radius: 4px;
                padding: 6px;
                color: {config.Colors.TEXT};
                font-size: 12px;
            }}
            
            QLineEdit:focus {{
                border-color: {config.Colors.PRIMARY};
                border-width: 2px;
            }}
            
            QPushButton {{
                background-color: {config.Colors.PRIMARY};
                color: white;
                border: none;
                padding: 8px 14px;
                border-radius: 5px;
                font-weight: 500;
                min-height: 30px;
            }}
            
            QPushButton:hover {{
                background-color: {config.Colors.PRIMARY_LIGHT};
            }}
            
            QComboBox {{
                background-color: {config.Colors.WIDGET};
                border: 1px solid {config.Colors.BORDER};
                border-radius: 5px;
                padding: 6px 10px;
                min-height: 30px;
            }}
            
            QCheckBox {{
                color: {config.Colors.TEXT};
                spacing: 8px;
            }}
            
            QScrollArea {{
                border: none;
                background: transparent;
            }}
        """
        )
