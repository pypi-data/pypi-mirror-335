from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from typing import Optional, Union

from PyQt6.QtCore import Qt, QThread, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from annotation_tool import common, model

__ALL__ = ["update_settings"]


class CreateFileDialog(QDialog):
    def __init__(self, allowed_extensions, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.allowed_extensions = allowed_extensions
        self.selected_path = ""

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Create File")
        self.setMinimumSize(500, 250)

        layout = QVBoxLayout(self)

        # Directory selection
        self.directory_edit = QLineEdit(self)
        self.directory_edit.setReadOnly(True)
        layout.addWidget(QLabel("Select Directory:"))
        directory_button = QPushButton("Browse", self)
        directory_button.clicked.connect(self.selectDirectory)
        directory_layout = QHBoxLayout()
        directory_layout.addWidget(self.directory_edit)
        directory_layout.addWidget(directory_button)
        layout.addLayout(directory_layout)

        # Filename entry
        self.filename_edit = QLineEdit(self)
        layout.addWidget(QLabel("Filename:"))
        layout.addWidget(self.filename_edit)

        # Extension selection
        self.extension_combo = QComboBox(self)
        self.extension_combo.addItems(self.allowed_extensions)
        layout.addWidget(QLabel("Select file extension:"))
        layout.addWidget(self.extension_combo)

        # Buttons for dialog control
        buttons_layout = QHBoxLayout()
        create_button = QPushButton("Create", self)
        create_button.clicked.connect(self.createFile)
        cancel_button = QPushButton("Cancel", self)
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(create_button)
        buttons_layout.addWidget(cancel_button)

        layout.addLayout(buttons_layout)

    def selectDirectory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.directory_edit.setText(directory)

    def createFile(self):
        directory = self.directory_edit.text()
        filename = self.filename_edit.text().strip()
        extension = self.extension_combo.currentText()

        if not directory or not filename or not extension:
            QMessageBox.warning(
                self, "Incomplete Information", "Please specify all fields."
            )
            return

        full_path = Path(directory) / f"{filename}.{extension}"
        if full_path.exists():
            QMessageBox.critical(
                self,
                "File Exists",
                "The specified file already exists. Please choose a different name.",
            )
            return

        self.selected_path = str(full_path)
        self.accept()

    def getSelectedPath(self):
        return self.selected_path


class AdvancedFileSelector(QWidget):
    pathChanged = pyqtSignal(str)

    def __init__(
        self,
        name: str = None,
        must_exist=False,
        allowed_extensions=None,
        allow_file_selection=False,
        allow_directory_selection=False,
        allow_file_creation=False,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.name = name
        self.must_exist = must_exist

        # Allow extension to start with or without a dot
        if allowed_extensions is None:
            self.allowed_extensions = None
        else:
            self.allowed_extensions = [
                ext[1:] if ext.startswith(".") else ext for ext in allowed_extensions
            ]

        self.allow_file = allow_file_selection
        self.allow_directory = allow_directory_selection
        self.allow_file_creation = allow_file_creation

        self.current_path = ""

        self.init_ui()

    def init_ui(self):
        self.setMinimumSize(500, 50)
        layout = QHBoxLayout(self)

        if self.name:
            font = QFont()
            font.setPointSize(common.get_config().font_size)
            layout.addWidget(QLabel(f"{self.name}:"))

        # Create the line edit and button
        self.lineEdit = QLineEdit(self)
        self.lineEdit.setReadOnly(True)
        if self.must_exist:
            self.lineEdit.setPlaceholderText("Path must be set.")
        else:
            self.lineEdit.setPlaceholderText("No path set.")
        layout.addWidget(self.lineEdit)

        if self.allow_file:
            self.load_file_button = QPushButton("Load File", self)
            self.load_file_button.setFixedWidth(100)
            self.load_file_button.clicked.connect(self.loadFileDialog)
            layout.addWidget(self.load_file_button)

        if self.allow_directory:
            self.load_directory_button = QPushButton("Load Folder", self)
            self.load_directory_button.setFixedWidth(100)
            self.load_directory_button.clicked.connect(self.loadDirectoryDialog)
            layout.addWidget(self.load_directory_button)

        if self.allow_file_creation:
            self.create_button = QPushButton("Create File", self)
            self.create_button.setFixedWidth(100)
            self.create_button.clicked.connect(self.createFileDialog)
            layout.addWidget(self.create_button)

        self.setLayout(layout)

    def loadFileDialog(self):
        filter_string = self.createFilterString()
        path, _ = QFileDialog.getOpenFileName(self, "Select File", filter=filter_string)
        if path:
            if (
                self.allowed_extensions
                and Path(path).suffix[1:] not in self.allowed_extensions
            ):
                QMessageBox.critical(
                    self,
                    "Invalid File",
                    f"Invalid file extension. Allowed extensions are: {', '.join(self.allowed_extensions)}",
                )
                return
            self.setCurrentPath(path)

    def loadDirectoryDialog(self):
        path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if path:
            self.setCurrentPath(path)

    def createFileDialog(self):
        dialog = CreateFileDialog(self.allowed_extensions, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            path = dialog.getSelectedPath()
            if path:
                self.setCurrentPath(path)

    def createFilterString(self):
        if self.allowed_extensions:
            return (
                f"Files ({' '.join(['*.' + ext for ext in self.allowed_extensions])})"
            )
        return "All Files (*)"

    def getCurrentPath(self):
        return self.current_path

    def setCurrentPath(self, path, notify=True):
        self.current_path = path
        self.lineEdit.setText(path)
        if notify:
            self.pathChanged.emit(path)


class CustomListWidget(QListWidget):
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete:
            self.parent().remove_item()
        elif event.key() == Qt.Key.Key_F2:
            self.parent().rename_item()
        elif event.key() == Qt.Key.Key_Enter or event.key() == Qt.Key.Key_Return:
            if self.currentItem() is not None:
                self.parent().enter_current_item()
        elif (
            event.key() == Qt.Key.Key_Down
            and event.modifiers() == Qt.KeyboardModifier.ControlModifier
        ):
            self.parent().move_item_down()
        elif (
            event.key() == Qt.Key.Key_Up
            and event.modifiers() == Qt.KeyboardModifier.ControlModifier
        ):
            self.parent().move_item_up()
        elif (
            event.key() == Qt.Key.Key_A
            and event.modifiers() == Qt.KeyboardModifier.ControlModifier
        ):
            self.parent().add_item()
        else:
            super().keyPressEvent(event)

    def mouseDoubleClickEvent(self, event):
        item = self.itemAt(event.position().toPoint())
        if item is not None:
            self.parent().enter_current_item()
        super().mouseDoubleClickEvent(event)


class ModifyList(QWidget):
    additional_button_clicked = pyqtSignal(str)
    item_added = pyqtSignal(str)
    item_removed = pyqtSignal(str)
    item_renamed = pyqtSignal(str, str)
    order_changed = pyqtSignal(list)
    enter_item = pyqtSignal(str)

    def __init__(self, name: str, additional_buttons: Optional[list[str]] = None):
        super().__init__()
        self.name = name
        self.item_names = set()
        self.additional_buttons = additional_buttons or []
        self.init_ui()
        self.previous_order = self.current_order()

    def init_ui(self):
        layout = QVBoxLayout()
        self.list_widget = CustomListWidget(self)
        self.list_widget.model().rowsMoved.connect(self.check_order_changed)

        font = QFont()
        font.setPointSize(common.get_config().font_size)

        layout.addWidget(QLabel(self.name))
        layout.addWidget(self.list_widget)

        # enable drag and drop for reordering
        self.list_widget.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.list_widget.setDefaultDropAction(Qt.DropAction.MoveAction)

        buttons_layout = QHBoxLayout()
        add_button = QPushButton("&Add")
        add_button.setToolTip("Ctrl+A")
        remove_button = QPushButton("Remove")
        remove_button.setToolTip("Delete")
        rename_button = QPushButton("Rename")
        rename_button.setToolTip("F2")
        move_up_button = QPushButton("Move Up")
        move_up_button.setToolTip("Ctrl+Up")
        move_down_button = QPushButton("Move Down")
        move_down_button.setToolTip("Ctrl+Down")

        addional_buttons = [
            QPushButton(button_name) for button_name in self.additional_buttons
        ]

        buttons_layout.addWidget(add_button)
        buttons_layout.addWidget(remove_button)
        buttons_layout.addWidget(rename_button)
        buttons_layout.addWidget(move_up_button)
        buttons_layout.addWidget(move_down_button)
        for button in addional_buttons:
            buttons_layout.addWidget(button)

        layout.addLayout(buttons_layout)

        add_button.clicked.connect(self.add_item)
        remove_button.clicked.connect(self.remove_item)
        rename_button.clicked.connect(self.rename_item)
        move_up_button.clicked.connect(self.move_item_up)
        move_down_button.clicked.connect(self.move_item_down)
        for button in addional_buttons:
            button.clicked.connect(
                lambda _, name=button.text(): self.additional_button_clicked.emit(name)
            )

        self.setLayout(layout)

    def load_items(self, items: list[str]):
        self.item_names = set(items)
        self.list_widget.clear()
        font = QFont()
        font.setPointSize(common.get_config().font_size)
        for item in items:
            list_item = QListWidgetItem(item)
            list_item.setFont(font)
            self.list_widget.addItem(list_item)

    def add_item(self):
        while True:
            item_name, ok = QInputDialog.getText(
                self, "Add new item", "Enter new item (name must be unique):"
            )

            if ok:
                is_valid = item_name and item_name not in self.item_names

                if is_valid:
                    self.item_names.add(item_name)

                    font = QFont()
                    font.setPointSize(common.get_config().font_size)
                    new_item = QListWidgetItem(item_name)
                    new_item.setFont(font)
                    self.list_widget.addItem(new_item)

                    self.item_added.emit(item_name)
                    break
                if not is_valid:
                    QMessageBox.critical(
                        self,
                        "Invalid item",
                        f"Item with name '{item_name}' already exists or is the empty string. Please choose a different name.",
                    )
            else:
                break

    def remove_item(self):
        selected_item = self.list_widget.currentItem()
        if selected_item:
            item_name = selected_item.text()
            confirmation = QMessageBox.question(
                self,
                f"Remove {self.name}",
                f"Are you sure you want to remove '{item_name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if confirmation == QMessageBox.StandardButton.Yes:
                assert item_name in self.item_names
                self.item_names.remove(item_name)
                self.list_widget.takeItem(self.list_widget.row(selected_item))
                self.item_removed.emit(item_name)

    def rename_item(self):
        current_row = self.list_widget.currentRow()
        if current_row != -1:
            current_item = self.list_widget.item(current_row)
            old_name = current_item.text()

            while True:
                new_name, ok = QInputDialog.getText(
                    self,
                    "Rename item",
                    "Enter new item name (existing names are not allowed):",
                    text=old_name,
                )

                if not ok:
                    break  # Exit the loop if user cancels the dialog
                if new_name:
                    if new_name == old_name:
                        break  # Exit the loop if user enters the same name
                    if new_name not in self.item_names:
                        # All checks passed -> Rename the item
                        self.item_names.remove(old_name)
                        self.item_names.add(new_name)
                        current_item.setText(new_name)
                        self.item_renamed.emit(old_name, new_name)
                        break
                    else:
                        QMessageBox.critical(
                            self,
                            f"Invalid {self.name}",
                            f"{self.name} with name '{new_name}' already exists or is the empty string. Please choose a different name.",
                        )

    def current_order(self):
        return [
            self.list_widget.item(i).text() for i in range(self.list_widget.count())
        ]

    def check_order_changed(self):
        current_order = self.current_order()
        if current_order != self.previous_order:
            self.order_changed.emit(current_order)
            self.previous_order = current_order

    def move_item_up(self):
        current_row = self.list_widget.currentRow()
        if current_row >= 1:
            self.list_widget.insertItem(
                current_row - 1, self.list_widget.takeItem(current_row)
            )
            self.list_widget.setCurrentRow(current_row - 1)
            self.check_order_changed()

    def move_item_down(self):
        current_row = self.list_widget.currentRow()
        if current_row < self.list_widget.count() - 1:
            self.list_widget.insertItem(
                current_row + 1, self.list_widget.takeItem(current_row)
            )
            self.list_widget.setCurrentRow(current_row + 1)
            self.check_order_changed()

    @property
    def current_item(self) -> Optional[str]:
        current_row = self.list_widget.currentRow()
        if current_row == -1:
            return None
        return self.list_widget.item(current_row).text()

    def enter_current_item(self):
        current_item = self.current_item
        if current_item is not None:
            self.enter_item.emit(current_item)


class ModifyClassesDialog(QDialog):
    def __init__(
        self,
        annotation_group: model.AnnotationGroup,
        name_tracker: Optional[dict[str, str]] = None,
    ):
        super().__init__()
        self.group = annotation_group
        # new_name -> old_name, used to track name changes
        # new_name -> None, means the class is a new addition
        self.name_tracker = name_tracker or {
            class_name: name_tracker for class_name in self.group.classes
        }
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.modify_list_widget = ModifyList(name=f"{self.group.name} Classes")
        self.modify_list_widget.load_items(self.group.classes)
        self.modify_list_widget.item_added.connect(self.add_class)
        self.modify_list_widget.item_removed.connect(self.remove_class)
        self.modify_list_widget.item_renamed.connect(self.rename_class)
        self.modify_list_widget.order_changed.connect(self.rearrange_classes)
        layout.addWidget(self.modify_list_widget)

        self.exclusive_checkbox = QCheckBox("Exclusive")
        self.exclusive_checkbox.setChecked(self.group.exclusive)
        self.exclusive_checkbox.clicked.connect(
            lambda: self.set_exclusive(self.exclusive_checkbox.isChecked())
        )

        layout.addWidget(self.exclusive_checkbox)

        buttons_layout = QHBoxLayout()
        accept_button = QPushButton("Accept")
        cancel_button = QPushButton("Cancel")

        buttons_layout.addWidget(accept_button)
        buttons_layout.addWidget(cancel_button)
        layout.addLayout(buttons_layout)

        accept_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

        self.setLayout(layout)

    def add_class(self, class_name: str):
        self.group = replace(self.group, classes=self.group.classes + [class_name])
        self.name_tracker[class_name] = None  # Add new class to tracker
        print(f"Added Class: {class_name} => {self.group.classes}")

    def remove_class(self, class_name: str):
        self.group = replace(
            self.group, classes=[c for c in self.group.classes if c != class_name]
        )
        if class_name in self.name_tracker:
            del self.name_tracker[class_name]
        print(f"Removed Class: {class_name} => {self.group.classes}")

    def rename_class(self, old_name: str, new_name: str):
        self.group = replace(
            self.group,
            classes=[new_name if c == old_name else c for c in self.group.classes],
        )
        self.name_tracker[new_name] = self.name_tracker.pop(old_name)
        print(f"Renamed Class: {old_name} to {new_name} => {self.group.classes}")

    def rearrange_classes(self, new_order: list[str]):
        self.group = replace(self.group, classes=new_order)
        print(f"New order: {new_order} => {self.group.classes}")

    def set_exclusive(self, exclusive: bool):
        self.group = replace(self.group, exclusive=exclusive)
        print(f"Set Exclusive: {exclusive} => {self.group.exclusive}")


class LoadingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowModality(Qt.WindowModality.WindowModal)  # Set the dialog modality
        self.setWindowTitle("Loading")
        self.setGeometry(400, 400, 400, 200)  # Set dimensions of the dialog
        layout = QVBoxLayout(self)

        # Informative text
        self.label = QLabel(
            "Loading index, please wait...\nThis process may take a while depending on the data size."
        )
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

        # Progress bar (indeterminate state)
        self.progressBar = QProgressBar(self)
        self.progressBar.setRange(0, 0)  # Indeterminate mode
        layout.addWidget(self.progressBar)

        self.setMinimumDuration(3000)  # Minimum duration in milliseconds

    def setMinimumDuration(self, ms):
        self._min_duration = ms
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.accept)
        self._timer.start(ms)


class IndexLoader(QThread):
    finished = pyqtSignal(list, bool)

    def __init__(self, path: Path):
        super().__init__()
        self.path = path

    def run(self):
        timeout = False
        if self.path.is_dir():
            try:
                index = common.find_images_in_directory(
                    self.path,
                    recursive=True,
                    timeout_ms=common.get_config().indexing_timeout_sec * 1000,
                )
            except:  # noqa: E722
                # parsing the directory took too long
                index = []
                timeout = True
        else:
            df = common.df_from_file(self.path)
            index = df[common.PATH_COLUMN_NAME].apply(Path).tolist()
            
        self.finished.emit(index, timeout)


class UpdateProjectDialog(QDialog):
    def __init__(
        self, settings: Optional[model.ProjectSettings] = None, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        assert isinstance(settings, model.ProjectSettings) or settings is None

        self.is_new_project = settings is None
        self.settings = settings

        self.annotation_schema = (
            model.AnnotationSchema()
            if self.is_new_project
            else deepcopy(settings.schema)
        )

        # Mapping from current group names to their original names
        self.record_group_names = {
            group.name: group.name for group in self.annotation_schema.groups
        }
        # Mapping from group names to their class names
        self.record_class_names = {
            group.name: {class_name: class_name for class_name in group.classes}
            for group in self.annotation_schema.groups
        }

        self.init_ui()
        self.load_project_settings()
        self.connect_signals()

    def init_ui(self):
        self.setWindowTitle(
            "Create Project" if self.is_new_project else "Update Project"
        )
        self.main_layout = QVBoxLayout(self)

        # Initialize UI components with default settings
        self.init_project_name_ui()
        self.init_project_file_ui()
        self.init_file_index_selector_ui()
        self.init_output_file_selector_ui()
        self.init_annotation_schema_ui()
        self.init_buttons_ui()

    def init_project_name_ui(self):
        self.project_name_edit = QLineEdit()
        self.main_layout.addWidget(QLabel("Project Name:"))
        self.main_layout.addWidget(self.project_name_edit)

    def init_project_file_ui(self):
        self.project_file = AdvancedFileSelector(
            name="Project File",
            must_exist=True,
            allowed_extensions=["pkl"],
            allow_file_selection=False,
            allow_directory_selection=False,
            allow_file_creation=True,
        )
        self.main_layout.addWidget(self.project_file)

    def init_file_index_selector_ui(self):
        self.file_index_selector = AdvancedFileSelector(
            name="Input Index",
            must_exist=True,
            allowed_extensions=common.SUPPORTED_INDEX_FILE_EXTENSIONS,
            allow_file_selection=True,
            allow_directory_selection=True,
            allow_file_creation=False,
        )
        self.main_layout.addWidget(self.file_index_selector)

    def init_output_file_selector_ui(self):
        self.output_file_selector = AdvancedFileSelector(
            name="Export File (Optional)",
            must_exist=False,
            allowed_extensions=common.SUPPORTED_OUTPUT_FILE_EXTENSIONS,
            allow_file_selection=True,
            allow_directory_selection=False,
            allow_file_creation=True,
        )
        self.main_layout.addWidget(self.output_file_selector)

    def init_annotation_schema_ui(self):
        self.group_editor_widget = ModifyList("Annotation Groups", ["Edit Classes"])
        self.main_layout.addWidget(self.group_editor_widget)

    def init_buttons_ui(self):
        buttons_layout = QHBoxLayout()
        accept_button = QPushButton("Accept")
        cancel_button = QPushButton("Cancel")

        # Set object names for the buttons
        accept_button.setObjectName("AcceptButton")
        cancel_button.setObjectName("CancelButton")

        buttons_layout.addWidget(accept_button)
        buttons_layout.addWidget(cancel_button)
        self.main_layout.addLayout(buttons_layout)

        # Connect signals directly within the same method where buttons are defined
        accept_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

    def load_project_settings(self):
        if not self.is_new_project:
            self.project_name_edit.setText(self.settings.name)
            self.project_file.setCurrentPath(self.settings.file.as_posix(), False)
            self.file_index_selector.setCurrentPath("cannot be changed", False)
            self.file_index_selector.setEnabled(False)
            if self.settings.output_file:
                self.output_file_selector.setCurrentPath(
                    self.settings.output_file.as_posix(), False
                )
            self.group_editor_widget.load_items(self.settings.schema.group_names())

    def connect_signals(self):
        self.file_index_selector.pathChanged.connect(self.verify_input_index)
        self.output_file_selector.pathChanged.connect(self.verify_output_file)
        self.group_editor_widget.item_added.connect(self.add_annotation_group)
        self.group_editor_widget.item_removed.connect(self.remove_annotation_group)
        self.group_editor_widget.item_renamed.connect(self.rename_annotation_group)
        self.group_editor_widget.order_changed.connect(self.rearrange_annotation_schema)
        self.group_editor_widget.additional_button_clicked.connect(
            self.handle_additional_button
        )
        self.group_editor_widget.enter_item.connect(
            self.edit_classes_of_annotation_group
        )

    def add_annotation_group(self, group_name: str):
        new_group = model.AnnotationGroup(group_name, [], False)
        self.annotation_schema = self.annotation_schema.add_group(new_group)
        self.record_group_names[group_name] = None  # Add new group to tracker
        self.record_class_names[group_name] = {}

        print(f"Added Group: {new_group} => {self.annotation_schema.groups}")
        print(f"Group Names: {self.record_group_names}")

    def remove_annotation_group(self, group_name: str):
        self.annotation_schema = self.annotation_schema.remove_group(group_name)
        if group_name in self.record_group_names:
            del self.record_group_names[group_name]
            del self.record_class_names[group_name]
        print(f"Removed Group: {group_name} => {self.annotation_schema.groups}")
        print(f"Group Names: {self.record_group_names}")

    def rearrange_annotation_schema(self, new_order: list[str]):
        self.annotation_schema = self.annotation_schema.rearrange_names(new_order)
        print(f"New order: {new_order} => {self.annotation_schema.groups}")

    def rename_annotation_group(self, old_name: str, new_name: str):
        self.annotation_schema = self.annotation_schema.rename_group(old_name, new_name)
        print(
            f"Renamed Group: {old_name} to {new_name} => {self.annotation_schema.groups}"
        )
        self.record_group_names[new_name] = self.record_group_names.pop(old_name)
        self.record_class_names[new_name] = self.record_class_names.pop(old_name)

    def handle_additional_button(self, button_name: str):
        if button_name == "Edit Classes":
            group_name = self.group_editor_widget.current_item
            self.edit_classes_of_annotation_group(group_name)

    def edit_classes_of_annotation_group(self, group_name: str):
        print(f"Edit classes of {group_name=}")

        group = self.annotation_schema.get_group(group_name)
        tracker = self.record_class_names[group_name]
        dialog = ModifyClassesDialog(group, tracker)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.annotation_schema = self.annotation_schema.update_group(dialog.group)
            self.record_class_names[group_name] = (
                dialog.name_tracker
            )  # Update class names

            print(f"Updated Group: {group_name} => {self.annotation_schema.groups}")
            print(f"Updated Class Names: {self.record_class_names}")

    def verify_input_index(self, path: Union[str, Path]):
        if not path:
            return

        path = Path(path) if isinstance(path, str) else path

        if not path.exists():
            QMessageBox.critical(
                self, "Invalid Path", "The specified path does not exist."
            )
            self.file_index_selector.setCurrentPath("", False)
            return

        if path.is_dir():
            return  # Directories are allowed

        if path.suffix not in common.SUPPORTED_INDEX_FILE_EXTENSIONS:
            QMessageBox.critical(
                self,
                "Invalid File",
                f"Invalid file extension. Supported extensions are: {', '.join(common.SUPPORTED_INDEX_FILE_EXTENSIONS)}",
            )
            self.file_index_selector.setCurrentPath("", False)

        try:
            df = common.df_from_file(path)
            if common.PATH_COLUMN_NAME not in df.columns:
                raise ValueError(f"Column '{common.PATH_COLUMN_NAME}' not found.")
        except Exception as e:
            QMessageBox.critical(self, "Invalid File", f"Error reading file: {e}.")
            self.file_index_selector.setCurrentPath("", False)

    def verify_output_file(self, path: Union[str, Path]):
        if not path:
            return

        path = Path(path) if isinstance(path, str) else path

        if path.exists():
            if not path.is_file():
                QMessageBox.critical(
                    self, "Invalid Path", "The specified path is not a file."
                )
                self.output_file_selector.setCurrentPath("", False)
                return

            if path.suffix not in common.SUPPORTED_OUTPUT_FILE_EXTENSIONS:
                QMessageBox.critical(
                    self,
                    "Invalid File",
                    f"Invalid file extension. Supported extensions are: {', '.join(common.SUPPORTED_OUTPUT_FILE_EXTENSIONS)}",
                )
                self.output_file_selector.setCurrentPath("", False)

            # Warn user that the file will be overwritten
            confirmation = QMessageBox.question(
                self,
                "File Exists",
                "The specified file already exists. This file will be overwritten on the next save. Do you want to continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if confirmation == QMessageBox.StandardButton.No:
                self.output_file_selector.setCurrentPath("", False)

        else:
            # Check if the directory exists
            parent_dir = path.parent
            if not parent_dir.exists():
                QMessageBox.critical(
                    self, "Invalid Path", "The specified directory does not exist."
                )
                self.output_file_selector.setCurrentPath("", False)
                return

    def accept(self):
        if not self.validate_inputs():
            return  # Stop if validation fails

        if self.is_new_project:
            self.handle_new_project()
        else:
            self.update_existing_project()
            super().accept()

    def validate_inputs(self):
        # Validate project name
        project_name = self.project_name_edit.text().strip()
        if not project_name:
            QMessageBox.critical(
                self, "Incomplete Information", "Please specify the project name."
            )
            return False

        # Validate annotation schema
        if not self.annotation_schema.groups:
            QMessageBox.critical(
                self, "Incomplete Information", "Please specify at least one group."
            )
            return False

        # Validate index file path for new projects
        if self.is_new_project:
            index_path = self.file_index_selector.getCurrentPath()
            if not index_path:
                QMessageBox.critical(
                    self,
                    "Incomplete Information",
                    "Please specify the input index file.",
                )
                return False

        return True  # All validations passed

    def handle_new_project(self):
        index_path = self.file_index_selector.getCurrentPath()
        loader = IndexLoader(Path(index_path))
        loader.finished.connect(self.on_index_loaded)
        loader.start()
        self.loading_dialog = LoadingDialog(self)
        self.loading_dialog.exec()  # This will block until the loading is complete

    def on_index_loaded(self, index, timeout):
        if timeout:
            QMessageBox.critical(
                self,
                "Indexing Timeout",
                "Indexing took too long. Please try again with a smaller dataset, or increase the timeout duration in the settings.",
            )
            return

        if len(index) == 0:
            QMessageBox.critical(
                self,
                "Empty Index",
                "Indexing resulted in 0 files to annotate. Please check the input index file/directory.",
            )
            return

        output_file = self.output_file_selector.getCurrentPath() or None
        output_file = Path(output_file) if output_file else None
        project_file = Path(self.project_file.getCurrentPath())

        self.settings = model.ProjectSettings(
            name=self.project_name_edit.text(),
            file=project_file,
            schema=self.annotation_schema,
            file_paths=index,
            output_file=output_file,
        )
        super().accept()

    def update_existing_project(self):
        output_file = self.output_file_selector.getCurrentPath() or None
        output_file = Path(output_file) if output_file else None
        project_file = Path(self.project_file.getCurrentPath())

        self.settings = replace(
            self.settings,
            name=self.project_name_edit.text(),
            file=project_file,
            schema=self.annotation_schema,
            output_file=output_file,
        )


class OpenProjectDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("Open Project")
        self.init_ui()
        self.project = None

    def init_ui(self):
        layout = QVBoxLayout(self)

        self.file_selector = AdvancedFileSelector(
            name="Project File",
            must_exist=True,
            allowed_extensions=["pkl"],
            allow_file_selection=True,
            allow_directory_selection=False,
            allow_file_creation=False,
        )
        layout.addWidget(self.file_selector)

        # Buttons
        buttons_layout = QHBoxLayout()
        open_button = QPushButton("Open")
        cancel_button = QPushButton("Cancel")

        buttons_layout.addWidget(open_button)
        buttons_layout.addWidget(cancel_button)
        layout.addLayout(buttons_layout)

        open_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

    def accept(self):
        project_file = self.file_selector.getCurrentPath()
        try:
            self.project = model.Project.from_disk(project_file)
            super().accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading project: {e}")
            self.project = None
            self.file_selector.setCurrentPath("", False)
