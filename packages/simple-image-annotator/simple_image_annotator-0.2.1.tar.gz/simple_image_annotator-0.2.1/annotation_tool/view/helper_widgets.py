from pathlib import Path
import platform
import subprocess
from typing import Union

import OpenGL.GL as gl
from PIL import Image
import PyQt6.QtCore as qtc
from PyQt6.QtCore import Qt
import PyQt6.QtGui as qtg
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
import PyQt6.QtWidgets as qtw
import cv2
import numpy as np

from annotation_tool import common, model


def simulate_key_press(widget, key, modifier=Qt.KeyboardModifier.NoModifier):
    event = qtg.QKeyEvent(qtg.QKeyEvent.Type.KeyPress, key, modifier)
    qtw.QApplication.postEvent(widget, event)


def open_image_as_rgb(
    image_path: Union[str, Path],
    rotation: common.Rotation = common.Rotation.DEG_0,
    return_flipped: bool = False,
):
    image_path = image_path.as_posix() if isinstance(image_path, Path) else image_path

    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if image is None:
        raise FileNotFoundError(f"Image not found at the path: {image_path}")

    if len(image.shape) == 2:  # Grayscale image
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGBA)
    elif image.shape[2] == 3:  # RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGBA)
    elif image.shape[2] == 1:  # Grayscale
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGBA)
    elif image.shape[2] == 4:  # RGBA image, no need to convert
        pass

    if rotation == common.Rotation.DEG_90:
        image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    elif rotation == common.Rotation.DEG_180:
        image = cv2.rotate(image, cv2.ROTATE_180)
    elif rotation == common.Rotation.DEG_270:
        image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)

    if return_flipped:
        image = cv2.flip(image, 0)

    return image


def build_separator(orientation, parent=None):
    separator = qtw.QFrame(parent)
    if orientation == "horizontal":
        separator.setFrameShape(qtw.QFrame.Shape.HLine)
    elif orientation == "vertical":
        separator.setFrameShape(qtw.QFrame.Shape.VLine)
    else:
        raise ValueError("Invalid orientation: 'horizontal' or 'vertical' expected")

    separator.setFrameShadow(qtw.QFrame.Shadow.Sunken)
    return separator


class RangeIntValidator(qtg.QIntValidator):
    def __init__(self, lower_bound, upper_bound, parent=None):
        super(RangeIntValidator, self).__init__(lower_bound, upper_bound, parent)
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    def validate(self, input, pos):
        if input:
            try:
                value = int(input)
            except ValueError:
                return qtg.QValidator.State.Invalid, input, pos
            if self.lower_bound <= value <= self.upper_bound:
                return qtg.QIntValidator.State.Acceptable, input, pos
            else:
                return qtg.QIntValidator.State.Invalid, input, pos
        return qtg.QIntValidator.State.Intermediate, input, pos

    def setRange(self, lower_bound, upper_bound):
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound


class OpenGLGraphicsView(QOpenGLWidget):
    EPS = 1e-4

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scale_factor = 1.15
        self.min_scale = 1.0
        self.max_scale = 32
        self.current_scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.panning = False
        self.last_mouse_position = None
        self.texture_id = None
        self.texture_width = 0
        self.texture_height = 0

    def initializeGL(self):
        gl.glClearColor(0, 0, 0, 1)

    def paintGL(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)  # Always clear the screen
        if self.texture_id:
            gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture_id)
            self.draw_image()
        else:
            gl.glLoadIdentity()

    def clamp_offsets(self):
        bound = self.current_scale - 1
        self.offset_x = max(-bound, min(bound, self.offset_x))
        self.offset_y = max(-bound, min(bound, self.offset_y))

    def draw_image(self):
        if self.texture_id is None:
            return

        gl.glEnable(gl.GL_TEXTURE_2D)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture_id)

        self.clamp_offsets()

        # Apply transformations
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()

        # Translate for panning
        tx = self.offset_x
        ty = self.offset_y
        gl.glTranslatef(tx, ty, 0)

        # Scale the image
        gl.glScalef(self.current_scale, self.current_scale, 1)

        # Vertex and texture coordinates
        vertices = [-1, -1, 0, 1, -1, 0, 1, 1, 0, -1, 1, 0]
        tex_coords = [0, 0, 1, 0, 1, 1, 0, 1]

        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glEnableClientState(gl.GL_TEXTURE_COORD_ARRAY)

        gl.glVertexPointer(3, gl.GL_FLOAT, 0, vertices)
        gl.glTexCoordPointer(2, gl.GL_FLOAT, 0, tex_coords)

        gl.glDrawArrays(gl.GL_QUADS, 0, 4)

        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        gl.glDisableClientState(gl.GL_TEXTURE_COORD_ARRAY)

        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
        gl.glDisable(gl.GL_TEXTURE_2D)

    def wheelEvent(self, event):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            # Get the position of the mouse relative to the widget
            mouse_pos = event.position()
            scene_x_before = (mouse_pos.x() / self.width()) * 2 - 1 - self.offset_x
            scene_y_before = -((mouse_pos.y() / self.height()) * 2 - 1) - self.offset_y

            # Determine the scale direction
            if event.angleDelta().y() > 0 and self.current_scale < self.max_scale:
                new_scale = self.current_scale * self.scale_factor
            elif event.angleDelta().y() < 0 and self.current_scale > self.min_scale:
                new_scale = self.current_scale / self.scale_factor
            else:
                return  # No scaling to be done, exit early

            if new_scale <= self.min_scale + OpenGLGraphicsView.EPS:
                new_scale = self.min_scale
            if new_scale >= self.max_scale - OpenGLGraphicsView.EPS:
                new_scale = self.max_scale

            # new_scale = max(self.min_scale, min(self.max_scale, new_scale))

            # Calculate the new scene position after scaling
            scene_x_after = scene_x_before * (new_scale / self.current_scale)
            scene_y_after = scene_y_before * (new_scale / self.current_scale)

            # Update offsets to keep the mouse position stationary relative to the scene
            self.offset_x += scene_x_before - scene_x_after
            self.offset_y += scene_y_before - scene_y_after

            # Update the current scale
            self.current_scale = new_scale

            self.update()
        else:
            super().wheelEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton and self.current_scale > 1:
            self.panning = True
            self.last_mouse_position = event.position()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.panning:
            delta = event.position() - self.last_mouse_position
            self.last_mouse_position = event.position()
            self.offset_x += (delta.x() / self.width()) * 2 * 4 / 3 / self.current_scale
            self.offset_y -= (
                (delta.y() / self.height()) * 2 * 3 / 4 / self.current_scale
            )
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def load_image(self, image: np.ndarray):
        self.texture_height, self.texture_width, _ = image.shape

        # Generate a texture ID
        if self.texture_id is not None:
            gl.glDeleteTextures(1, [self.texture_id])
        self.texture_id = gl.glGenTextures(1)

        # Bind the texture ID
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture_id)

        # Set the texture parameters
        gl.glTexParameteri(
            gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR_MIPMAP_LINEAR
        )
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)

        # Upload the texture data to GPU
        gl.glTexImage2D(
            gl.GL_TEXTURE_2D,
            0,
            gl.GL_RGBA,
            self.texture_width,
            self.texture_height,
            0,
            gl.GL_RGBA,
            gl.GL_UNSIGNED_BYTE,
            image,
        )

        # Generate mipmaps
        gl.glGenerateMipmap(gl.GL_TEXTURE_2D)

        # Unbind the texture
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

    def reset(self):
        self.current_scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.update()

    def clear_image(self):
        if self.texture_id:
            gl.glDeleteTextures(1, [self.texture_id])
            self.texture_id = None
        self.update()  # Request a repaint


class ImageViewer(qtw.QWidget):
    resetFocus = qtc.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.view = OpenGLGraphicsView(self)
        self.error_label = qtw.QLabel()
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_image_label = qtw.QLabel()
        self.no_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.stacked_widget = qtw.QStackedWidget()
        self.stacked_widget.addWidget(self.view)
        self.stacked_widget.addWidget(self.error_label)
        self.stacked_widget.addWidget(self.no_image_label)

        self.setLayout(qtw.QVBoxLayout())
        self.layout().addWidget(self.stacked_widget)

        self.current_widget = None
        self.current_image = None
        self.image_width, self.image_height = None, None
        self.keep_aspect_ratio = False

        self._update_current_widget(self.no_image_label)

    def _update_current_widget(self, widget):
        if widget != self.current_widget:
            self.stacked_widget.setCurrentWidget(widget)
            self.current_widget = widget

    def set_image(self, image: model.Image):
        assert isinstance(image, model.Image)

        self.clear()
        self.current_image = image

        image_path = image.file
        rotation = image.rotation

        if not image.exists():
            self.error_label.setText(
                f"Image not found: {image_path}.\nPlease check if the file still exists or was renamed."
            )
            self._update_current_widget(self.error_label)
            return

        try:
            self._update_current_widget(self.view)
            image = open_image_as_rgb(image_path, rotation, return_flipped=True)
            self.current_rotation = rotation
            self.image_width, self.image_height = image.shape[1], image.shape[0]
            self.view.load_image(image)
            self.view.update()
            self._adjust_view_size()
        except Exception as e:
            self.error_label.setText(
                f"Error loading image: {image_path}.\nPlease check if the file is a valid image.\n\nErrorMsg: {e}"
            )
            self._update_current_widget(self.error_label)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.current_widget == self.view:
            self.view.update()
            self._adjust_view_size()

    def clear(self):
        self.current_image = None
        self.image_width, self.image_height = None, None
        self._update_current_widget(self.no_image_label)
        if self.current_widget == self.view:
            self.view.clear_image()
            self.view.update()

    def set_keep_aspect_ratio(self, keep_aspect_ratio: bool):
        if keep_aspect_ratio == self.keep_aspect_ratio:
            return

        # Do not handle this in _adjust_view_size() as this is the only place where we need to handle this
        if not keep_aspect_ratio:
            self.view.resize(self.width(), self.height())
            self.view.move(0, 0)

        self.keep_aspect_ratio = keep_aspect_ratio
        self.view.update()
        self._adjust_view_size()

    def _adjust_view_size(self):
        if not self.keep_aspect_ratio or self.current_image is None:
            return

        view_size = self.view.size()
        image_ratio = self.image_width / self.image_height
        view_ratio = view_size.width() / view_size.height()

        if view_ratio > image_ratio:
            new_width = int(view_size.height() * image_ratio)
            new_height = view_size.height()
        else:
            new_width = view_size.width()
            new_height = int(view_size.width() / image_ratio)

        self.view.resize(new_width, new_height)
        self.view.move(
            (self.stacked_widget.width() - new_width) // 2,
            (self.stacked_widget.height() - new_height) // 2,
        )

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.resetFocus.emit()

        if (
            event.button() == Qt.MouseButton.RightButton
            and self.current_image is not None
            and self.current_widget is not None
            and self.current_widget == self.view
        ):

            menu = qtw.QMenu(self)
            reset_action = menu.addAction("Reset")
            rotate_clockwise = menu.addAction("Rotate Clockwise")
            rotate_counter_clockwise = menu.addAction("Rotate Counter Clockwise")
            open_in_image_viewer = menu.addAction("Open in Image Viewer")
            open_in_file_explorer = menu.addAction("Open in File Explorer")

            action = menu.exec(event.globalPosition().toPoint())

            if action == reset_action:
                self.current_image.rotation = common.Rotation.DEG_0
                self.set_image(self.current_image)

            if action == rotate_clockwise:
                new_rotation = common.rotate(self.current_image.rotation, True)
                self.current_image.rotation = new_rotation
                self.set_image(self.current_image)

            if action == rotate_counter_clockwise:
                new_rotation = common.rotate(self.current_image.rotation, False)
                self.current_image.rotation = new_rotation
                self.set_image(self.current_image)

            if action == open_in_image_viewer:
                file = self.current_image.file
                file_path = Path(file)

                assert file_path.is_file(), f"File not found: {file_path}"
                try:
                    Image.open(file_path).show()
                except Exception as e:
                    print(f"Error opening in image viewer: {file_path}")
                    print(e)

            if action == open_in_file_explorer:
                file = self.current_image.file
                file_dir = Path(file).parent

                assert file_dir.is_dir(), f"Directory not found: {file_dir}"

                try:
                    if platform.system() == "Windows":
                        subprocess.Popen(f'explorer /select, "{file}"')
                    elif platform.system() == "Darwin":
                        subprocess.Popen(["open", file_dir])
                    else:
                        subprocess.Popen(["xdg-open", file_dir])
                except Exception as e:
                    print(f"Error opening in explorer: {file_dir}")
                    print(e)

        super().mousePressEvent(event)
