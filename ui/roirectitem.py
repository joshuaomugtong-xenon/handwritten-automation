from __future__ import annotations
from typing import TYPE_CHECKING

from PyQt6.QtWidgets import (
    QApplication,
    QGraphicsRectItem,
    QGraphicsItem,
    QLineEdit,
    QGroupBox,
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

from modules.config import ROI_MIME_TYPE

if TYPE_CHECKING:
    from .MainWindow import MainWindow


class ROIRectItem(QGraphicsRectItem):

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, None)

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

        self.owner: MainWindow = None
        self.template_groupbox: QGroupBox = None
        self.data_groupbox: QGroupBox = None

        self.x1: QLineEdit = None
        self.y1: QLineEdit = None
        self.x2: QLineEdit = None
        self.y2: QLineEdit = None

    def scroll_to_template_groupbox(self):
        if self.template_groupbox is not None:
            self.owner.scroll_to_template_groupbox(self.template_groupbox)

    def scroll_to_data_groupbox(self):
        if self.data_groupbox is not None:
            self.owner.scroll_to_data_groupbox(self.data_groupbox)

    def itemChange(self, change, value):
        if change == QGraphicsRectItem.GraphicsItemChange.ItemSelectedChange:
            if value:
                self.set_selected(True)
                if self.edit_mode:
                    pass
                else:
                    self.show_highlight()
            else:
                self.set_selected(False)
                if self.edit_mode:
                    self.set_edit_mode(False)
                else:
                    self.hide_highlight()
        return super().itemChange(change, value)

    def set_selected(self, selected: bool):
        if selected:
            self.owner.photo_viewer.viewer.selected_item = self
        else:
            self.owner.photo_viewer.viewer.selected_item = None

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
            # Scroll to data groupbox
            self.scroll_to_data_groupbox()
            # Scroll to template groupbox
            self.scroll_to_template_groupbox()
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
            if self.is_resizing and self.current_handle:
                # Only handle resizing and moving in edit mode
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

                # Update text input fields
                scene_rect = self.mapRectToScene(self.rect())
                x1, y1, x2, y2 = scene_rect.getCoords()
                if self.x1 is not None:
                    self.x1.setText(str(int(x1)))
                if self.y1 is not None:
                    self.y1.setText(str(int(y1)))
                if self.x2 is not None:
                    self.x2.setText(str(int(x2)))
                if self.y2 is not None:
                    self.y2.setText(str(int(y2)))
            elif self.is_moving:
                delta = event.pos() - event.lastPos()
                self.moveBy(delta.x(), delta.y())
                self.update_resize_handles()

                # Update text input fields
                scene_rect = self.mapRectToScene(self.rect())
                x1, y1, x2, y2 = scene_rect.getCoords()
                if self.x1 is not None:
                    self.x1.setText(str(int(x1)))
                if self.y1 is not None:
                    self.y1.setText(str(int(y1)))
                if self.x2 is not None:
                    self.x2.setText(str(int(x2)))
                if self.y2 is not None:
                    self.y2.setText(str(int(y2)))
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
            # Set cursor to pointing hand if selected but not in edit mode
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
            if isinstance(item, ROIRectItem) and item != self:
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
