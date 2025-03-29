import math
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QVBoxLayout,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsPixmapItem,
    QFrame,
    QMenu,
)
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QPixmap,
    QCursor,
)
from PyQt6.QtCore import (
    Qt,
    QPoint,
    pyqtSignal,
    QRectF,
    QPropertyAnimation,
    QEasingCurve,
    QVariantAnimation,
    QDataStream,
    QIODevice,
)

from .RegionBox import RegionBox

from modules.config import ROI_MIME_TYPE


SCALE_FACTOR = 1.25
ANIMATION_DURATION = 300  # Animation duration in milliseconds


class PhotoViewer(QGraphicsView):
    coordinates_changed = pyqtSignal(QPoint)
    region_created = pyqtSignal(QRectF)

    def __init__(self, parent):
        super().__init__(parent)
        self._zoom = 0
        self._pinned = False
        self._empty = True
        self._scene = QGraphicsScene(self)
        self._photo = QGraphicsPixmapItem()
        self._photo.setShapeMode(QGraphicsPixmapItem.ShapeMode.BoundingRectShape)
        # self._photo.setTransformationMode(Qt.SmoothTransformation)
        self._scene.addItem(self._photo)
        self.setScene(self._scene)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QBrush(QColor(30, 30, 30)))
        self.setFrameShape(QFrame.Shape.NoFrame)
        # For animation
        self._animation = None

        # Set focus policy to accept keyboard events
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def keyPressEvent(self, event):
        # To do: Add keyboard shortcuts for copy, paste, delete
        return super().keyPressEvent(event)

    def has_photo(self):
        return not self._empty

    def reset_view(self, scale=1):
        rect = QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            if (scale := max(1, scale)) == 1:
                self._zoom = 0
            if self.has_photo():
                unity = self.transform().mapRect(QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = scale * min(
                    viewrect.width() / scenerect.width(),
                    viewrect.height() / scenerect.height()
                )
                self.scale(factor, factor)
                if not self.zoom_pinned():
                    self.centerOn(self._photo)
                self.update_coordinates()

    def set_photo(self, pixmap: QPixmap = None):
        if pixmap and not pixmap.isNull():
            self._empty = False
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            self._photo.setPixmap(pixmap)
        else:
            self._empty = True
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
            self._photo.setPixmap(QPixmap())
        if not (self.zoom_pinned() and self.has_photo()):
            self._zoom = 0
        self.reset_view(SCALE_FACTOR ** self._zoom)

    def zoom_level(self):
        return self._zoom

    def zoom_to_rect(self, rect: QRectF):
        # Cancel any ongoing animation
        if self._animation and self._animation.state() == QPropertyAnimation.State.Running:
            self._animation.stop()

        # Store initial view state
        init_trfm = self.transform()
        init_h_scroll = self.horizontalScrollBar().value()
        init_v_scroll = self.verticalScrollBar().value()

        # Reset zoom to initial state if needed
        if self._zoom != 0:
            self.reset_view()
            self._zoom = 0

        # Create a copy of the target rectangle
        target_rect = QRectF(rect)

        # Modify the target rect so it is zoomed out by 33%
        target_rect.adjust(
            -target_rect.width() / 3,
            -target_rect.height() / 3,
            target_rect.width() / 3,
            target_rect.height() / 3
        )

        # Calculate target transformation
        self.fitInView(target_rect, Qt.AspectRatioMode.KeepAspectRatio)
        trgt_trfm = self.transform()

        # Calculate target scroll positions
        target_center = target_rect.center()
        viewport_center = self.viewport().rect().center()
        mapped_center = self.mapFromScene(target_center)
        trgt_h_scroll = self.horizontalScrollBar().value() \
            + (mapped_center.x() - viewport_center.x())
        trgt_v_scroll = self.verticalScrollBar().value() \
            + (mapped_center.y() - viewport_center.y())

        # Reset to initial transform
        self.setTransform(init_trfm)
        self.horizontalScrollBar().setValue(init_h_scroll)
        self.verticalScrollBar().setValue(init_v_scroll)

        # Create animation for the transform
        self._animation = QVariantAnimation()
        self._animation.setDuration(ANIMATION_DURATION)

        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation.setStartValue(0.0)
        self._animation.setEndValue(1.0)

        # Define animation update function
        def updateTransform(prog):
            # Interpolate transform
            m11 = init_trfm.m11() + prog * (trgt_trfm.m11() - init_trfm.m11())
            m12 = init_trfm.m12() + prog * (trgt_trfm.m12() - init_trfm.m12())
            m13 = init_trfm.m13() + prog * (trgt_trfm.m13() - init_trfm.m13())
            m21 = init_trfm.m21() + prog * (trgt_trfm.m21() - init_trfm.m21())
            m22 = init_trfm.m22() + prog * (trgt_trfm.m22() - init_trfm.m22())
            m23 = init_trfm.m23() + prog * (trgt_trfm.m23() - init_trfm.m23())
            m31 = init_trfm.m31() + prog * (trgt_trfm.m31() - init_trfm.m31())
            m32 = init_trfm.m32() + prog * (trgt_trfm.m32() - init_trfm.m32())
            m33 = init_trfm.m33() + prog * (trgt_trfm.m33() - init_trfm.m33())

            crnt_trfm = self.transform()
            crnt_trfm.setMatrix(m11, m12, m13, m21, m22, m23, m31, m32, m33)
            self.setTransform(crnt_trfm)

            # Interpolate scroll positions
            h_scroll = init_h_scroll + prog * (trgt_h_scroll - init_h_scroll)
            v_scroll = init_v_scroll + prog * (trgt_v_scroll - init_v_scroll)
            self.horizontalScrollBar().setValue(int(h_scroll))
            self.verticalScrollBar().setValue(int(v_scroll))

        # Connect animation to update function
        self._animation.valueChanged.connect(updateTransform)

        # Connect animation finished signal
        def onAnimationFinished():

            # Calculate the equivalent zoom level based on the scale
            current_scale = trgt_trfm.m11()  # Horizontal scale factor

            if current_scale > 1.0:
                # Calculate how many zoom steps this represents
                steps = round(
                    math.log(current_scale) / math.log(SCALE_FACTOR))
                self._zoom = steps
            elif current_scale < 1.0:
                # For zooming out
                steps = round(
                    math.log(1.0 / current_scale) / math.log(SCALE_FACTOR))
                self._zoom = -steps
            else:
                self._zoom = 0

            # Update the view
            self.update()

        self._animation.finished.connect(onAnimationFinished)

        # Start the animation
        self._animation.start()

    def zoom_pinned(self):
        return self._pinned

    def set_zoom_pinned(self, enable):
        self._pinned = bool(enable)

    def zoom(self, step: int):
        step = int(step)
        zoom = max(0, self._zoom + step)
        if zoom != self._zoom:
            self._zoom = zoom
            if self._zoom > 0:
                if step > 0:
                    factor = SCALE_FACTOR ** step
                else:
                    factor = 1 / SCALE_FACTOR ** abs(step)
                self.scale(factor, factor)
            else:
                self.reset_view()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        self.zoom(delta and delta // abs(delta))

    def resizeEvent(self, event):
        super().resizeEvent(event)

    def toggle_drag_mode(self):
        if self.dragMode() == QGraphicsView.DragMode.ScrollHandDrag:
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
        elif not self._photo.pixmap().isNull():
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

    def update_coordinates(self, pos=None):
        if self._photo.isUnderMouse():
            if pos is None:
                pos = self.mapFromGlobal(QCursor.pos())
            point = self.mapToScene(pos).toPoint()
        else:
            point = QPoint()
        self.coordinates_changed.emit(point)

    def mouseMoveEvent(self, event):
        self.update_coordinates(event.pos())
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        self.coordinates_changed.emit(QPoint())
        super().leaveEvent(event)

    def contextMenuEvent(self, event):
        # Only show context menu if we have a photo loaded
        if not self.has_photo():
            return

        # Create context menu
        menu = QMenu()

        # Check if an ROI item is under the cursor
        item = self.scene().itemAt(self.mapToScene(event.pos()), self.transform())
        if isinstance(item, RegionBox):
            # Edit
            edit_action = menu.addAction("Edit")
            edit_action.setEnabled(not item.edit_mode)
            # Copy
            copy_action = menu.addAction("Copy")
            # Delete
            delete_action = menu.addAction("Delete")

            # Show the menu and get selected action
            selected_action = menu.exec(event.globalPos())
            if selected_action == edit_action:
                item.setSelected(True)
                item.set_edit_mode(True)
            elif selected_action == copy_action:
                item.copy_to_clipboard()
            elif selected_action == delete_action:
                item.delete_region()
            event.accept()
        else:
            # New
            new_action = menu.addAction("New")
            # If clipboard has ROI data, enable paste action
            paste_action = menu.addAction("Paste")

            clipboard = QApplication.clipboard()
            mime_data = clipboard.mimeData()
            paste_action.setEnabled(mime_data.hasFormat(ROI_MIME_TYPE))
            # Show the context menu
            action = menu.exec(event.globalPos())
            # Handle the selected action
            pos = self.mapToScene(event.pos())

            if action == new_action:
                # Create new ROI
                # Default size for new ROI
                w, h = 100.0, 100.0
                x = pos.x() - w/2
                y = pos.y() - h/2

                self.region_created.emit(QRectF(x, y, w, h))

            elif action == paste_action:
                # Paste ROI
                byte_array = mime_data.data(ROI_MIME_TYPE)
                stream = QDataStream(byte_array, QIODevice.OpenModeFlag.ReadOnly)

                _ = stream.readDouble()
                _ = stream.readDouble()
                w = stream.readDouble()
                h = stream.readDouble()

                x = pos.x() - w/2
                y = pos.y() - h/2

                region = RegionBox(x, y, w, h)
                self.region_created.emit(region)

    def unselect_all(self):
        for item in self._scene.items():
            if isinstance(item, RegionBox):
                item.setSelected(False)


class PhotoViewerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.viewer = PhotoViewer(self)
        self.viewer.coordinates_changed.connect(self.handle_coordinates)
        self.coordinates_label = QLabel(self)
        layout = QVBoxLayout(self)
        layout.addWidget(self.viewer)
        layout.addWidget(
            self.coordinates_label,
            alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setContentsMargins(0, 0, 0, 0)

    def handle_coordinates(self, point: QPoint):
        if not point.isNull():
            self.coordinates_label.setText(f'{point.x()}, {point.y()}')
        else:
            self.coordinates_label.clear()


def main():
    pass


if __name__ == '__main__':
    main()
