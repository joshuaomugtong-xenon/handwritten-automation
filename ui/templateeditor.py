from __future__ import annotations
from typing import TYPE_CHECKING

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QLayout,
    QGroupBox,
    QFormLayout,
)
from PyQt6.QtGui import (
    QRegularExpressionValidator,
)
from PyQt6.QtCore import (
    Qt,
    QRegularExpression,
)

from modules.template_validation import Template, Region

if TYPE_CHECKING:
    from .MainWindow import MainWindow

from .ROIRectItem import ROIRectItem


class Label(QLabel):
    def __init__(self, text: str = ''):
        super().__init__(text, parent=None)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)


class TextInput(QLineEdit):
    def __init__(self, text: str = '', width: int = 500):
        super().__init__(text, parent=None)
        self.setStyleSheet('background-color: white; color: black;')
        self.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setFixedWidth(width)
        self.setPlaceholderText('Enter text')


class PositiveIntegerInput(QLineEdit):
    def __init__(self, text: str = '', width: int = 120):
        super().__init__(text, parent=None)
        self.setStyleSheet('background-color: white; color: black;')
        self.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setFixedWidth(width)
        pattern = r"^([0-9]|[1-9][0-9]|[1-9][0-9]{2}|[1-9][0-9]{3}|10000)$"
        self.setValidator(
            QRegularExpressionValidator(QRegularExpression(pattern)))
        self.setPlaceholderText('0-10000')


class BooleanInput(QLineEdit):
    def __init__(self, text: str = '', width: int = 120):
        super().__init__(text, parent=None)
        self.setStyleSheet('background-color: white; color: black;')
        self.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setFixedWidth(width)
        yaml_bool_pattern = r"^(true|false|yes|no|on|off|y|n)$"
        self.setValidator(
            QRegularExpressionValidator(
                QRegularExpression(yaml_bool_pattern, QRegularExpression.PatternOption.CaseInsensitiveOption)))
        self.setPlaceholderText('true, false, yes, no')


class TypeInput(QLineEdit):
    def __init__(self, text: str = '', width: int = 500):
        super().__init__(text, parent=None)
        self.setStyleSheet('background-color: white; color: black;')
        self.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setFixedWidth(width)
        pattern = r"^(text|encirclement|checkbox)$"
        self.setValidator(
            QRegularExpressionValidator(QRegularExpression(pattern)))
        self.setPlaceholderText('text, encirclement, checkbox')


class ClickableLabel(QLabel):
    def __init__(self, text: str = ''):
        super().__init__(text, parent=None)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setStyleSheet('text-decoration: italic;')
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.owner: MainWindow = None
        self.rect_item: ROIRectItem = None

    def zoom_to_rect(self):
        if self.rect_item is not None and self.owner is not None:
            self.owner.photo_viewer.viewer.zoom_to_rect(
                self.rect_item.rect())
            self.rect_item.setSelected(True)
            self.owner.photo_viewer.viewer._scene.update()

    def mousePressEvent(self, event):
        self.zoom_to_rect()
        super().mousePressEvent(event)


class TemplateWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._layout = QVBoxLayout()
        self.setLayout(self._layout)
        self.region_layout = None

    def init_ui(self, template: Template):
        self.reset_layout()
        ui_handles: dict[str, QLineEdit] = {}

        groupbox = QGroupBox('')
        self._layout.addWidget(groupbox)
        groupbox_layout = QFormLayout()
        groupbox.setLayout(groupbox_layout)

        for name, info in template.model_fields.items():
            type_ = info.annotation
            value = getattr(template, name)

            if type_ == str:
                input_widget = TextInput(value)
            elif type_ == int:
                input_widget = PositiveIntegerInput(str(value))
            elif type_ == bool:
                input_widget = BooleanInput(str(value))
            else:
                # Skip unsupported types
                continue

            label = Label(title(name))
            groupbox_layout.addRow(label, input_widget)
            ui_handles[name] = input_widget

        groupbox = QGroupBox('Regions')
        self._layout.addWidget(groupbox)
        groupbox_layout = QVBoxLayout()
        groupbox.setLayout(groupbox_layout)
        self.region_layout = groupbox_layout

        return ui_handles

    def add_region(
            self,
            region: Region,
            use_coords: bool = True,
            ):

        ui_handles: dict[str, QLineEdit | list[QLineEdit]] = {}

        groupbox = QGroupBox('')
        self.region_layout.addWidget(groupbox)
        groupbox_layout = QFormLayout()
        groupbox.setLayout(groupbox_layout)

        groupbox_layout.addRow(
            Label('Name'),
            handle := TextInput(region.name))
        ui_handles['name'] = handle
        groupbox_layout.addRow(
            Label('Type'),
            handle := TypeInput(region.type))
        ui_handles['type'] = handle
        link = None
        if use_coords:
            handles: list[QLineEdit] = []
            label = Label('Coordinates')
            layout = QHBoxLayout()
            groupbox_layout.addRow(label, layout)
            for coord in region.coordinates:
                layout.addWidget(
                    handle := PositiveIntegerInput(str(coord), 120))
                handles.append(handle)
            ui_handles['coordinates'] = handles
            link = ClickableLabel('Click to view')
            layout.addWidget(link)
        else:
            handles: list[QLineEdit] = []
            label = Label('Markers')
            layout = QHBoxLayout()
            groupbox_layout.addRow(label, layout)
            for marker in region.markers:
                layout.addWidget(
                    handle := PositiveIntegerInput(str(marker), 120))
                handles.append(handle)
            ui_handles['markers'] = handles

        return ui_handles, groupbox, link

    def remove_region(self, groupbox: QGroupBox):
        self.region_layout.removeWidget(groupbox)
        groupbox.hide()
        groupbox.deleteLater()

    def reset_layout(self):
        self.clear_layout(self._layout)

    def clear_layout(self, layout: QLayout = None):
        if layout is None:
            layout = self.layout()
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                child_layout = item.layout()
                if child_layout is not None:
                    self.clear_layout(child_layout)
                    child_layout.deleteLater()


def title(string: str) -> str:
    return ' '.join([word.capitalize() for word in string.split('_')])
