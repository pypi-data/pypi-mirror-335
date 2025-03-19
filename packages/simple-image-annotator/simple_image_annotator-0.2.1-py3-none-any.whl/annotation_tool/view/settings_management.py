from PyQt6.QtCore import Qt
from PyQt6.QtGui import QValidator
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)

from annotation_tool import common, model
from annotation_tool.view.helper_widgets import RangeIntValidator


class GroupClassSeparatorValidator(QValidator):
    def validate(self, input: str, pos: int):
        # Disallow common CSV separators: comma, semicolon, tab, space
        forbidden = {",", ";", "\t", " "}
        if any(char in forbidden for char in input):
            return (QValidator.State.Invalid, input, pos)
        if len(input) == 0:
            return (QValidator.State.Intermediate, input, pos)
        return (QValidator.State.Acceptable, input, pos)


class CustomSpinBox(QSpinBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def step_size(self):
        return super().singleStep()

    def stepBy(self, steps):
        current_value = self.value()
        new_value = (current_value // self.step_size + steps) * self.step_size
        new_value = max(self.minimum(), min(new_value, self.maximum()))
        self.setValue(new_value)


class SettingsDialog(QDialog):
    def __init__(self, config: model.Config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setMinimumSize(300, 250)
        self.init_ui()

    def init_ui(self):
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setWindowFlag(Qt.WindowType.WindowMinimizeButtonHint, False)
        self.setWindowFlag(Qt.WindowType.WindowMaximizeButtonHint, False)
        self.setWindowFlag(Qt.WindowType.WindowTitleHint, False)
        self.setWindowFlag(Qt.WindowType.WindowMinMaxButtonsHint, False)

        self.setWindowTitle("Settings")
        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # Font Size
        self.font_size_spinbox = QSpinBox()
        self.font_size_spinbox.setRange(6, 14)
        self.font_size_spinbox.lineEdit().setReadOnly(True)
        self.font_size_spinbox.setValue(self.config.font_size)
        form_layout.addRow("Font Size:", self.font_size_spinbox)

        # Keep Aspect Ratio
        self.keep_aspectratio_checkbox = QCheckBox("Keep Aspect Ratio")
        self.keep_aspectratio_checkbox.setChecked(self.config.keep_aspectratio)
        form_layout.addRow("Keep Aspect Ratio:", self.keep_aspectratio_checkbox)

        # Autosave Interval (seconds)
        self.autosave_interval_spinbox = CustomSpinBox()
        self.autosave_interval_spinbox.setRange(30, 300)  # 30 seconds to 5 minutes
        self.autosave_interval_spinbox.setSingleStep(10)
        self.autosave_interval_spinbox.lineEdit().setReadOnly(True)
        self.autosave_interval_spinbox.setValue(self.config.autosave_interval_sec)
        form_layout.addRow("Autosave Interval (sec):", self.autosave_interval_spinbox)

        # Indexing Timeout (seconds)
        self.indexing_timeout_spinbox = CustomSpinBox()
        self.indexing_timeout_spinbox.setRange(5, 60)
        self.indexing_timeout_spinbox.setSingleStep(5)
        self.autosave_interval_spinbox.lineEdit().setReadOnly(True)
        self.indexing_timeout_spinbox.setValue(self.config.indexing_timeout_sec)
        form_layout.addRow("Indexing Timeout (sec):", self.indexing_timeout_spinbox)

        # Group Class Separator
        self.group_class_separator_lineedit = QLineEdit(
            self.config.group_class_separator
        )
        self.group_class_separator_lineedit.setValidator(GroupClassSeparatorValidator())
        self.group_class_separator_lineedit.setMaxLength(5)
        self.group_class_separator_lineedit.setPlaceholderText(
            common.GROUP_CLASS_SEPARATOR
        )
        form_layout.addRow(
            "Group-Class Separator:", self.group_class_separator_lineedit
        )

        main_layout.addLayout(form_layout)

        # Buttons
        buttons_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(cancel_button)

        main_layout.addLayout(buttons_layout)
        self.setLayout(main_layout)

    def accept(self):
        group_class_sep = self.group_class_separator_lineedit.text()
        if group_class_sep == "":
            group_class_sep = common.GROUP_CLASS_SEPARATOR

        self.config = model.Config(
            previous_project=self.config.previous_project,
            font_size=self.font_size_spinbox.value(),
            keep_aspectratio=self.keep_aspectratio_checkbox.isChecked(),
            autosave_interval_sec=self.autosave_interval_spinbox.value(),
            indexing_timeout_sec=self.indexing_timeout_spinbox.value(),
            group_class_separator=group_class_sep,
        )
        super().accept()
