import math
from typing import TYPE_CHECKING
from PyQt5.QtWidgets import (
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
from PyQt5.QtGui import (
    QBrush,
    QColor,
    QPixmap,
    QCursor,
)
from PyQt5.QtCore import (
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

if TYPE_CHECKING:
    from main import ProjectApp

from .roirectitem import ROIRectItem
from modules.template_validation import Region


SCALE_FACTOR = 1.25
ANIMATION_DURATION = 300  # Animation duration in milliseconds
ROI_MIME_TYPE = 'application/x-roi-rectangle'


class PhotoViewer(QGraphicsView):
    coordinatesChanged = pyqtSignal(QPoint)

    def __init__(self, parent):
        super().__init__(parent)
        self._zoom = 0
        self._pinned = False
        self._empty = True
        self._scene = QGraphicsScene(self)
        self._photo = QGraphicsPixmapItem()
        self._photo.setShapeMode(QGraphicsPixmapItem.BoundingRectShape)
        # self._photo.setTransformationMode(Qt.SmoothTransformation)
        self._scene.addItem(self._photo)
        self.setScene(self._scene)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QBrush(QColor(30, 30, 30)))
        self.setFrameShape(QFrame.NoFrame)
        # For animation
        self._animation = None
        self.owner: ProjectApp = None

    def hasPhoto(self):
        return not self._empty

    def resetView(self, scale=1):
        rect = QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            if (scale := max(1, scale)) == 1:
                self._zoom = 0
            if self.hasPhoto():
                unity = self.transform().mapRect(QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = scale * min(
                    viewrect.width() / scenerect.width(),
                    viewrect.height() / scenerect.height()
                )
                self.scale(factor, factor)
                if not self.zoomPinned():
                    self.centerOn(self._photo)
                self.updateCoordinates()

    def setPhoto(self, pixmap=None):
        if pixmap and not pixmap.isNull():
            self._empty = False
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self._photo.setPixmap(pixmap)
        else:
            self._empty = True
            self.setDragMode(QGraphicsView.NoDrag)
            self._photo.setPixmap(QPixmap())
        if not (self.zoomPinned() and self.hasPhoto()):
            self._zoom = 0
        self.resetView(SCALE_FACTOR ** self._zoom)

    def zoomLevel(self):
        return self._zoom

    def zoomToRect(self, rect: QRectF):
        # Cancel any ongoing animation
        if self._animation and \
                self._animation.state() == QPropertyAnimation.Running:
            self._animation.stop()

        # Store initial view state
        init_trfm = self.transform()
        init_h_scroll = self.horizontalScrollBar().value()
        init_v_scroll = self.verticalScrollBar().value()

        # Temporarily disable scroll bars to prevent flickering during
        # animation
        h_policy = self.horizontalScrollBarPolicy()
        v_policy = self.verticalScrollBarPolicy()
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Reset zoom to initial state if needed
        if self._zoom != 0:
            self.resetView()
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
        self.fitInView(target_rect, Qt.KeepAspectRatio)
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
        self._animation.setEasingCurve(QEasingCurve.OutCubic)
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

        # Connect animation finished signal to restore scrollbar policies
        def onAnimationFinished():
            self.setHorizontalScrollBarPolicy(h_policy)
            self.setVerticalScrollBarPolicy(v_policy)

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

    def zoomPinned(self):
        return self._pinned

    def setZoomPinned(self, enable):
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
                self.resetView()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        self.zoom(delta and delta // abs(delta))

    def resizeEvent(self, event):
        super().resizeEvent(event)

    def toggleDragMode(self):
        if self.dragMode() == QGraphicsView.ScrollHandDrag:
            self.setDragMode(QGraphicsView.NoDrag)
        elif not self._photo.pixmap().isNull():
            self.setDragMode(QGraphicsView.ScrollHandDrag)

    def updateCoordinates(self, pos=None):
        if self._photo.isUnderMouse():
            if pos is None:
                pos = self.mapFromGlobal(QCursor.pos())
            point = self.mapToScene(pos).toPoint()
        else:
            point = QPoint()
        self.coordinatesChanged.emit(point)

    def mouseMoveEvent(self, event):
        self.updateCoordinates(event.pos())
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        self.coordinatesChanged.emit(QPoint())
        super().leaveEvent(event)

    def contextMenuEvent(self, event):
        # Only show context menu if we have a photo loaded
        if not self.hasPhoto():
            return

        # Create context menu
        menu = QMenu()

        # Check if an ROI item is under the cursor
        item = self.scene().itemAt(
            self.mapToScene(event.pos()), self.transform())
        if isinstance(item, ROIRectItem):
            # Edit
            edit_action = menu.addAction("Edit")
            edit_action.setEnabled(not item.edit_mode)
            # Copy and Delete
            copy_action = menu.addAction("Copy")
            delete_action = menu.addAction("Delete")
            # Show the menu and get selected action
            selected_action = menu.exec(event.pos())
            if selected_action == edit_action:
                item.setSelected(True)
                item.set_edit_mode(True)
            elif selected_action == copy_action:
                item.copy_to_clipboard()
            elif selected_action == delete_action:
                self._scene.removeItem(item)
                gb = item.template_groupbox
                if gb is not None:
                    # Find and remove the corresponding UI handles from
                    # template_regions
                    for i, region_dict in enumerate(
                            self.owner.template_regions):
                        if any(field for field in region_dict.values()
                                if hasattr(field, 'parent') and
                                field.parent() == gb):
                            del self.owner.template_regions[i]
                            break
                    self.owner.template_editor.remove_region(gb)
                    item.template_groupbox = None

            event.accept()
        else:
            # Add new ROI action
            new_action = menu.addAction("New")
            # If clipboard has ROI data, add paste action
            clipboard = QApplication.clipboard()
            mime_data = clipboard.mimeData()
            paste_action = menu.addAction("Paste")
            paste_action.setEnabled(mime_data.hasFormat(ROI_MIME_TYPE))
            # Show the context menu
            action = menu.exec(event.globalPos())
            # Handle the selected action
            if action == new_action:
                # Add new ROI
                roi = self.new_ROI(event.pos())
                loc = [int(a) for a in roi.rect().getCoords()]
                region = Region(
                    name='',
                    type='text',
                    coordinates=loc,
                    markers=loc,
                )
                ui_handles, gb, link = self.owner.template_editor.add_region(
                    region)
                self.owner.template_regions.append(ui_handles)
                x1, y1, x2, y2 = ui_handles['coordinates']
                roi.x1 = x1
                roi.y1 = y1
                roi.x2 = x2
                roi.y2 = y2
                roi.template_groupbox = gb
                roi.owner = self.owner
                link.owner = self.owner
                link.rect_item = roi

            elif action == paste_action:
                # Paste ROI
                roi = self.paste_ROI(event.pos())
                loc = [int(a) for a in roi.rect().getCoords()]
                region = Region(
                    name='',
                    type='text',
                    coordinates=loc,
                    markers=loc,
                )
                ui_handles, gb, link = self.owner.template_editor.add_region(
                    region)
                self.owner.template_regions.append(ui_handles)
                x1, y1, x2, y2 = ui_handles['coordinates']
                roi.x1 = x1
                roi.y1 = y1
                roi.x2 = x2
                roi.y2 = y2
                roi.template_groupbox = gb
                roi.owner = self.owner
                link.owner = self.owner
                link.rect_item = roi

    def new_ROI(self, pos):
        if not self.hasPhoto():
            return

        # If no position specified, use center of viewport
        if pos is None:
            viewport_center = self.viewport().rect().center()
            pos = viewport_center

        # Convert to scene coordinates
        scene_pos = self.mapToScene(pos)

        # Default size for new ROI
        width, height = 100, 100
        x = scene_pos.x() - width/2
        y = scene_pos.y() - height/2

        roi = ROIRectItem(x, y, width, height)
        self._scene.addItem(roi)
        roi.setSelected(True)
        roi.set_edit_mode(True)

        return roi

    def paste_ROI(self, pos):
        if not self.hasPhoto():
            return

        # Get ROI data from clipboard
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()

        byte_array = mime_data.data(ROI_MIME_TYPE)
        stream = QDataStream(byte_array, QIODevice.ReadOnly)

        # Read ROI data
        _ = stream.readDouble()
        _ = stream.readDouble()
        width = stream.readDouble()
        height = stream.readDouble()

        # Convert to scene coordinates for target position
        scene_pos = self.mapToScene(pos)

        # Offset the ROI to be centered at the paste position
        new_x = scene_pos.x() - width/2
        new_y = scene_pos.y() - height/2

        roi = ROIRectItem(new_x, new_y, width, height)
        self._scene.addItem(roi)
        roi.setSelected(True)
        roi.set_edit_mode(True)

        return roi


class PhotoViewerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.viewer = PhotoViewer(self)
        self.viewer.coordinatesChanged.connect(self.handleCoords)
        self.labelCoords = QLabel(self)
        self.labelCoords.setStyleSheet("background: rgba(255, 0, 0, 0);")
        layout = QVBoxLayout(self)
        layout.addWidget(self.viewer)
        layout.addWidget(
            self.labelCoords,
            alignment=Qt.AlignRight | Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setContentsMargins(0, 0, 0, 0)

    def handleCoords(self, point: QPoint):
        if not point.isNull():
            self.labelCoords.setText(f'{point.x()}, {point.y()}')
        else:
            self.labelCoords.clear()


def main():
    pass


if __name__ == '__main__':
    main()
