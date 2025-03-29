from PyQt6.QtWidgets import (
    QApplication,
    QGraphicsRectItem,
    QGraphicsItem,
)
from PyQt6.QtCore import (
    Qt,
    QRectF,
    QByteArray,
    QDataStream,
    QIODevice,
    QMimeData,
)
from PyQt6.QtGui import (
    QPen,
    QBrush,
    QColor,
)
from PyQt6.QtCore import (
    pyqtSignal,
    QObject,
)

from modules.config import ROI_MIME_TYPE


class RegionBoxSignals(QObject):
    request_scroll_to_template_groupbox = pyqtSignal()
    request_scroll_to_data_groupbox = pyqtSignal()
    request_delete_region = pyqtSignal()
    coordinates_changed = pyqtSignal(int, int, int, int)


class RegionBox(QGraphicsRectItem):

    def __init__(
            self,
            x: float,
            y: float,
            w: float,
            h: float,
            ):

        super().__init__(x, y, w, h, None)

        # Set flags to enable mouse interaction
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        self.setAcceptedMouseButtons(Qt.MouseButton.LeftButton | Qt.MouseButton.RightButton)

        # Default colors
        self.normal_color = QColor(52, 152, 219, 102)  # RGBA: ~40% opacity
        self.normal_border = QColor(52, 152, 219, 255)  # 100% opacity
        self.selected_color = QColor(52, 152, 219, 178)  # ~70% opacity
        self.handle_fill_color = QColor(41, 128, 185, 255)
        self.handle_border_color = QColor(236, 240, 241, 255)

        # Initial appearance
        self.setBrush(QBrush(self.normal_color))
        self.setPen(QPen(self.normal_border, 2))

        # Signals
        self.signals = RegionBoxSignals()

        # Edit mode flag
        self.edit_mode = False

        # Resize handles
        self.handle_size = 8
        self.handle_space = 4
        self.handles: dict[str, tuple[QGraphicsRectItem, Qt.CursorShape]] = {}
        self.update_resize_handles()
        self.hide_handles()
        self.hide_highlight()

        self.is_resizing = False
        self.is_moving = False
        self.current_handle = None
        self.start_rect = None
        self.start_pos = None

    def itemChange(self, change, value):
        if change == QGraphicsRectItem.GraphicsItemChange.ItemSelectedChange:
            if value:
                if self.edit_mode:
                    pass
                else:
                    self.show_highlight()
            else:
                if self.edit_mode:
                    self.set_edit_mode(False)
                else:
                    self.hide_highlight()
        return super().itemChange(change, value)

    def copy_to_clipboard(self):
        rect = self.rect()

        # Create a byte array to store the ROI data
        byte_array = QByteArray()
        stream = QDataStream(byte_array, QIODevice.OpenModeFlag.WriteOnly)

        # Write rectangle properties to the stream
        stream.writeDouble(rect.x())
        stream.writeDouble(rect.y())
        stream.writeDouble(rect.width())
        stream.writeDouble(rect.height())

        # Create mime data and send it to clipboard
        mime_data = QMimeData()
        mime_data.setData(ROI_MIME_TYPE, byte_array)
        QApplication.clipboard().setMimeData(mime_data)

    def delete_region(self):
        # Emit signal to request deletion of this region
        # MainWindow will handle the deletion
        # The connected function needs a reference to this RegionBox
        self.signals.request_delete_region.emit()

    def set_edit_mode(self, enable: bool):
        self.edit_mode = enable
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, enable)
        if enable:
            self.bring_to_front()
            # Show handles and highlight when in edit mode
            self.show_highlight()
            for handle, _ in self.handles.values():
                handle.show()
        else:
            # Hide handles when exiting edit mode
            self.hide_highlight()
            for handle, _ in self.handles.values():
                handle.hide()
        self.update()  # Refresh appearance
        self.scene().update()  # Refresh scene

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.signals.request_scroll_to_template_groupbox.emit()
            self.signals.request_scroll_to_data_groupbox.emit()
            if self.edit_mode:
                # Resize enabled only in edit mode
                for name, (handle, cursor) in self.handles.items():
                    if handle.contains(event.pos()):
                        self.is_resizing = True
                        self.current_handle = name
                        self.start_rect = self.rect()
                        self.start_pos = event.pos()
                        event.accept()
                        return
                self.is_moving = True
        elif event.button() == Qt.MouseButton.RightButton:
            if not self.isSelected():
                self.setSelected(True)

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.edit_mode:
                self.is_resizing = False
                self.current_handle = None
                self.is_moving = False
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if self.edit_mode:
            # Only handle resizing and moving in edit mode
            if self.is_resizing and self.current_handle:
                # If resizing, calculate new rectangle based on handle position
                delta = event.pos() - self.start_pos
                rect = QRectF(self.start_rect)
                if 'T' in self.current_handle:
                    top = rect.top() + delta.y()
                    rect.setTop(top)
                    if top > rect.bottom():
                        self.current_handle.replace('T', 'B')
                if 'B' in self.current_handle:
                    bottom = rect.bottom() + delta.y()
                    rect.setBottom(bottom)
                    if bottom < rect.top():
                        self.current_handle.replace('B', 'T')
                if 'L' in self.current_handle:
                    left = rect.left() + delta.x()
                    rect.setLeft(left)
                    if left > rect.right():
                        self.current_handle.replace('L', 'R')
                if 'R' in self.current_handle:
                    right = rect.right() + delta.x()
                    rect.setRight(right)
                    if right < rect.left():
                        self.current_handle.replace('R', 'L')
                norm_rect = rect.normalized()
                self.setRect(norm_rect)
                self.update_resize_handles()

                # Update text input fields by emitting a signal
                # (needs to be connected in MainWindow!)
                scene_rect = self.mapRectToScene(self.rect())
                x1, y1, x2, y2 = scene_rect.getCoords()
                self.signals.coordinates_changed.emit(int(x1), int(y1), int(x2), int(y2))
            elif self.is_moving:
                delta = event.pos() - event.lastPos()
                self.moveBy(delta.x(), delta.y())
                self.update_resize_handles()

                # Update text input fields by emitting a signal
                # (needs to be connected in MainWindow!)
                scene_rect = self.mapRectToScene(self.rect())
                x1, y1, x2, y2 = scene_rect.getCoords()
                self.signals.coordinates_changed.emit(int(x1), int(y1), int(x2), int(y2))
            else:
                super().mouseMoveEvent(event)

    def hoverMoveEvent(self, event):
        if self.edit_mode:
            # Initially set cursor to size all
            self.setCursor(Qt.CursorShape.SizeAllCursor)
            # Then check if cursor is under a resize handle
            for handle, cursor in self.handles.values():
                if handle.contains(event.pos()):
                    self.setCursor(cursor)
                    break
        else:
            # Set cursor to pointing hand if not in edit mode
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        super().hoverMoveEvent(event)

    def hoverLeaveEvent(self, event):
        self.unsetCursor()
        super().hoverLeaveEvent(event)

    def show_highlight(self):
        self.setBrush(QBrush(self.selected_color))
        self.setPen(QPen(self.normal_border, 3))
        self.update()

    def hide_highlight(self):
        self.setBrush(QBrush(self.normal_color))
        self.setPen(QPen(self.normal_border, 2))
        self.update()

    def show_handles(self):
        for handle, _ in self.handles.values():
            handle.show()
        self.update()

    def hide_handles(self):
        for handle, _ in self.handles.values():
            handle.hide()
        self.update()

    def bring_to_front(self):
        # Find the highest Z-value in the scene
        highest_z = 1  # Start at 1 as default ROI Z-value

        for item in self.scene().items():
            if isinstance(item, RegionBox) and item != self:
                highest_z = max(highest_z, item.zValue())

        # Set this ROI's Z-value higher than the highest
        self.setZValue(highest_z + 1)
        self.update()

    def update_resize_handles(self):
        s = self.handle_size
        k = self.handle_space
        rect = self.rect()
        t, b, l, r = rect.top(), rect.bottom(), rect.left(), rect.right()
        cx, cy = rect.center().x(), rect.center().y()
        locations = {
            # Corners
            'TL': (
                (l - s + k, t - s + k, s, s),
                Qt.CursorShape.SizeFDiagCursor),
            'TR': (
                (r - k, t - s + k, s, s),
                Qt.CursorShape.SizeBDiagCursor),
            'BL': (
                (l - s + k, b - k, s, s),
                Qt.CursorShape.SizeBDiagCursor),
            'BR': (
                (r - k, b - k, s, s),
                Qt.CursorShape.SizeFDiagCursor),
            # Middle points (sides)
            'T': (
                (cx - s/2, t - s + k, s, s),
                Qt.CursorShape.SizeVerCursor),
            'R': (
                (r - k, cy - s/2, s, s),
                Qt.CursorShape.SizeHorCursor),
            'B': (
                (cx - s/2, b - k, s, s),
                Qt.CursorShape.SizeVerCursor),
            'L': (
                (l - s + k, cy - s/2, s, s),
                Qt.CursorShape.SizeHorCursor)
        }

        if not self.handles:
            for name, (location, cursor) in locations.items():
                x, y, w, h = location
                rect_item = QGraphicsRectItem(x, y, w, h, self)
                rect_item.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable, False)
                rect_item.setBrush(QBrush(self.handle_fill_color))
                rect_item.setPen(QPen(self.handle_border_color))

                self.handles[name] = (rect_item, cursor)
        else:
            for name, (rect_item, _) in self.handles.items():
                (x, y, w, h), _ = locations[name]
                rect_item.setRect(x, y, w, h)
