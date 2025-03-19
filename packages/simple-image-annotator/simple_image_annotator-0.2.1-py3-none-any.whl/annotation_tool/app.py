from typing import Optional, Union

import PyQt6.QtCore as qtc
from PyQt6.QtCore import Qt
import PyQt6.QtGui as qtg
import PyQt6.QtWidgets as qtw

from annotation_tool import common, model
from annotation_tool.view import (
    GUI,
    OpenProjectDialog,
    SettingsDialog,
    UpdateProjectDialog,
)


class MainApplication(qtw.QApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.position = None
        self.project: model.Project = None

        # timer for automatic saving
        self.save_timer = qtc.QTimer()
        self.save_timer.timeout.connect(self.save_project)
        self.save_timer.start(common.get_config().autosave_interval_sec * 1000)

        # setup design
        self.initTheme()
        self.gui = GUI()

        # Connect gui signals
        self.gui.jump_to[common.JumpType].connect(self.handleJump)
        self.gui.jump_to[int].connect(self.handleJump)
        self.gui.filterChanged.connect(self.filterChanged)

        # Connect gui shortcuts
        self.gui.save_shortcut.activated.connect(self.save_project)
        self.gui.left_shortcut.activated.connect(
            lambda: self.handleJump(common.JumpType.PREV)
        )
        self.gui.right_shortcut.activated.connect(
            lambda: self.handleJump(common.JumpType.NEXT)
        )
        self.gui.reload_shortcut.activated.connect(self.filterChanged)

        # Connect menu actions
        self.gui.new_project_action.triggered.connect(self.create_project)
        self.gui.open_project_action.triggered.connect(self.open_project)
        self.gui.update_project_action.triggered.connect(self.update_project)
        self.gui.save_project_action.triggered.connect(self.save_project)
        self.gui.settings_action.triggered.connect(self.open_settings)
        self.gui.close_project_action.triggered.connect(self.close_project)
        self.gui.exit_action.triggered.connect(self.quit)

        self.gui.show()

        # open recent project
        project = None
        if common.get_config().previous_project:
            try:
                project = model.Project.from_disk(common.get_config().previous_project)
            except Exception as e:
                print(f"Failed to load project: {e}")

        try:
            self._init_project(project)
        except Exception as e:
            print(f"Failed to initialize project: {e}")
            self._init_project(None)

    def _init_project(
        self, project: Optional[model.Project], target_position: Optional[int] = None
    ):
        self.project = project
        self.gui.clear()

        new_file = project.settings.file if self.project else None
        common.write_config(common.get_config().update_project(new_file))

        if self.project is not None:
            self.project.filter = model.Filter.from_schema(self.project.settings.schema)
            self.gui.setSchema(self.project.settings.schema)
            self.gui.setFilter(self.project.filter)
            self.gui.resetFocus()
            if target_position is None:
                self.handleJump(common.JumpType.FIRST_EMPTY, force=True)
            else:
                self.handleJump(target_position, force=True)

    def create_project(self):
        dlg = UpdateProjectDialog()
        if dlg.exec() == qtw.QDialog.DialogCode.Accepted:
            self._init_project(model.Project(dlg.settings))

    def update_project(self):
        project = self.project

        if project is None:
            return

        assert isinstance(project, model.Project)

        dlg = UpdateProjectDialog(self.project.settings)
        if dlg.exec() == qtw.QDialog.DialogCode.Accepted:
            updated_settings = dlg.settings
            translate_groups = dlg.record_group_names
            translate_classes = dlg.record_class_names
            is_identity = common.is_identity_mapping(translate_groups) and all(
                common.is_identity_mapping(v) for v in translate_classes.values()
            )

            if updated_settings == project.settings and is_identity:
                return  # nothing changed

            project.settings = updated_settings
            project.apply_renaming_mapping(translate_groups, translate_classes)
            project.to_disk()

            if updated_settings.schema == project.settings.schema and is_identity:
                # Schema did not change -> Keep current position
                self._init_project(project, self.position)
            elif project.filter.active:
                # Moving from filter to no filter -> Jump to first empty annotation
                self._init_project(project)
            else:
                # Moving from no filter to filter -> Keep current position
                self._init_project(project, self.position)

    def open_project(self):
        dlg = OpenProjectDialog()
        if dlg.exec() == qtw.QDialog.DialogCode.Accepted:
            self._init_project(dlg.project)

    def close_project(self, *args, **kwargs):
        self._init_project(None, None)

    def open_settings(self):
        config = common.get_config()
        dlg = SettingsDialog(config)
        if dlg.exec() == qtw.QDialog.DialogCode.Accepted:
            new_config = dlg.config
            if new_config != config:
                common.write_config(new_config)
                self.gui.updateSettings()
                self.save_timer.setInterval(new_config.autosave_interval_sec * 1000)

    def save_project(self):
        if self.project:
            self.project.to_disk()
            project_path = self.project.settings.file.as_posix()
            self.gui.writeStatusBar(f"Saved project to {project_path}.")

    @property
    def num_annotations(self) -> int:
        return len(self.project) if self.project else 0

    @property
    def current_annotation(self) -> model.Annotation:
        return self.project[self.position].annotation

    @property
    def current_image(self) -> model.Image:
        return self.project[self.position].image

    def _jump_abs(self, new_pos, force=False):
        if force:
            self.position = None

        new_pos = max(0, min(len(self.project) - 1, new_pos))  # clamp to valid range
        if new_pos != self.position:
            self.position = new_pos
            self.gui.setPosition(new_pos, len(self.project))
            self.gui.setAnnotation(self.current_annotation)
            self.gui.setImage(self.current_image)

    def _find_first_empty_annotation(self):
        # Really slow, but should be fine for now
        for idx, anno in enumerate(self.project.annotations):
            if anno.is_empty():
                return idx
        return 0

    def handleJump(self, target: Union[common.JumpType, int], force: bool = False):
        if self.project:
            if target == common.JumpType.START:
                self._jump_abs(0, force)
            elif target == common.JumpType.PREV:
                self._jump_abs(self.position - 1, force)
            elif target == common.JumpType.NEXT:
                self._jump_abs(self.position + 1, force)
            elif target == common.JumpType.END:
                self._jump_abs(len(self.project) - 1, force)
            elif target == common.JumpType.FIRST_EMPTY:
                self._jump_abs(self._find_first_empty_annotation(), force)
            elif isinstance(target, int):
                self._jump_abs(target, force)
            else:
                raise RuntimeError(f"Unknown jump target: {target}")

    def initTheme(self):
        font = qtg.QFont()
        font.setPointSize(common.get_config().font_size)
        self.setFont(font)

        self.setStyle("Fusion")

        # # Now use a palette to switch to dark colors:
        dark_palette = qtg.QPalette(self.style().standardPalette())
        dark_palette.setColor(qtg.QPalette.ColorRole.Window, qtg.QColor(53, 53, 53))
        dark_palette.setColor(qtg.QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        dark_palette.setColor(qtg.QPalette.ColorRole.Base, qtg.QColor(35, 35, 35))
        dark_palette.setColor(
            qtg.QPalette.ColorRole.AlternateBase, qtg.QColor(53, 53, 53)
        )
        dark_palette.setColor(
            qtg.QPalette.ColorRole.ToolTipBase, qtg.QColor(25, 25, 25)
        )
        dark_palette.setColor(qtg.QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        dark_palette.setColor(qtg.QPalette.ColorRole.Text, Qt.GlobalColor.white)
        dark_palette.setColor(qtg.QPalette.ColorRole.Button, qtg.QColor(53, 53, 53))
        dark_palette.setColor(qtg.QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        dark_palette.setColor(qtg.QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        dark_palette.setColor(qtg.QPalette.ColorRole.Link, qtg.QColor(42, 130, 218))
        dark_palette.setColor(
            qtg.QPalette.ColorRole.Highlight, qtg.QColor(42, 130, 218)
        )
        dark_palette.setColor(
            qtg.QPalette.ColorRole.HighlightedText, qtg.QColor(35, 35, 35)
        )
        dark_palette.setColor(
            qtg.QPalette.ColorGroup.Active,
            qtg.QPalette.ColorRole.Button,
            qtg.QColor(53, 53, 53),
        )
        dark_palette.setColor(
            qtg.QPalette.ColorGroup.Disabled,
            qtg.QPalette.ColorRole.ButtonText,
            Qt.GlobalColor.darkGray,
        )
        dark_palette.setColor(
            qtg.QPalette.ColorGroup.Disabled,
            qtg.QPalette.ColorRole.WindowText,
            Qt.GlobalColor.darkGray,
        )
        dark_palette.setColor(
            qtg.QPalette.ColorGroup.Disabled,
            qtg.QPalette.ColorRole.Text,
            Qt.GlobalColor.darkGray,
        )
        dark_palette.setColor(
            qtg.QPalette.ColorGroup.Disabled,
            qtg.QPalette.ColorRole.Light,
            qtg.QColor(53, 53, 53),
        )
        self.setPalette(dark_palette)

    def filterChanged(self):
        if self.project is not None:
            self.project.apply_filter()
            self.handleJump(common.JumpType.FIRST_EMPTY, force=True)
